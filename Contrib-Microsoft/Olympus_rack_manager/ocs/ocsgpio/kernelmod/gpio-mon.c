// Copyright (C) Microsoft Corporation. All rights reserved.
//
// This program is free software; you can redistribute it
// and/or modify it under the terms of the GNU General Public License
// as published by the Free Software Foundation; either version 2
// of the License, or (at your option) any later version.


#include <linux/init.h>
#include <linux/module.h>
#include <linux/kernel.h>
#include <linux/signal.h>
#include <linux/pid.h>
#include <linux/sched.h>
#include <linux/gpio.h>                 // Required for the GPIO functions
#include <linux/interrupt.h>            // Required for the IRQ code

#include <ocsgpio.h>
#include <ocsgpio-rmmap.h>
#include <gpiomon-usrhdlr.h>

MODULE_LICENSE("GPL");
MODULE_AUTHOR("Microsoft Corp");
MODULE_DESCRIPTION("Kernel module to catch gpio interrupts and alert user space");
MODULE_VERSION("0.1");

static char module_name[] = GPIOMON_MODULE_NAME;

const unsigned int gpioid_portpresence[MAX_PORT_GPIOCOUNT] = {
	GPIO_PORTPRESENCE_1, GPIO_PORTPRESENCE_2, GPIO_PORTPRESENCE_3, GPIO_PORTPRESENCE_4, 
    GPIO_PORTPRESENCE_5, GPIO_PORTPRESENCE_6, GPIO_PORTPRESENCE_7, GPIO_PORTPRESENCE_8, 
    GPIO_PORTPRESENCE_9, GPIO_PORTPRESENCE_10, GPIO_PORTPRESENCE_11, GPIO_PORTPRESENCE_12, 
    GPIO_PORTPRESENCE_13, GPIO_PORTPRESENCE_14, GPIO_PORTPRESENCE_15, GPIO_PORTPRESENCE_16, 
    GPIO_PORTPRESENCE_17, GPIO_PORTPRESENCE_18, GPIO_PORTPRESENCE_19, GPIO_PORTPRESENCE_20, 
    GPIO_PORTPRESENCE_21, GPIO_PORTPRESENCE_22, GPIO_PORTPRESENCE_23, GPIO_PORTPRESENCE_24, 
    GPIO_PORTPRESENCE_25, GPIO_PORTPRESENCE_26, GPIO_PORTPRESENCE_27, GPIO_PORTPRESENCE_28, 
    GPIO_PORTPRESENCE_29, GPIO_PORTPRESENCE_30, GPIO_PORTPRESENCE_31, GPIO_PORTPRESENCE_32, 
    GPIO_PORTPRESENCE_33, GPIO_PORTPRESENCE_34, GPIO_PORTPRESENCE_35, GPIO_PORTPRESENCE_36, 
    GPIO_PORTPRESENCE_37, GPIO_PORTPRESENCE_38, GPIO_PORTPRESENCE_39, GPIO_PORTPRESENCE_40, 
    GPIO_PORTPRESENCE_41, GPIO_PORTPRESENCE_42, GPIO_PORTPRESENCE_43, GPIO_PORTPRESENCE_44, 
    GPIO_PORTPRESENCE_45, GPIO_PORTPRESENCE_46, GPIO_PORTPRESENCE_47, GPIO_PORTPRESENCE_48
};
unsigned int gpio_irqcache[MAX_PORT_GPIOCOUNT];

static int usrpid;
static int sigid;
module_param(usrpid, int, S_IRUGO | S_IWUSR);
module_param(sigid, int, S_IRUGO | S_IWUSR);

/* Function prototype for the custom IRQ handler function -- see below for the implementation */
static irq_handler_t  gpio_irq_handler(unsigned int irq, void *dev_id, struct pt_regs *regs);

/******************************************************************************
*   Function Name: gpiomod_init
*   Purpose: Module initialization function - sets up IRQs for GPIO
*******************************************************************************/
static int __init gpiomod_init(void)
{
	int rc = 0;
	unsigned int count;
	unsigned int irqNumber;

	printk(KERN_DEBUG "%s: Starting gpio monitor module from PID=%d\n", module_name, usrpid);
	 
	for (count=0; (count < MAX_PORT_GPIOCOUNT); count++) {		
		irqNumber = gpio_to_irq( gpioid_portpresence[count] );	
		
		/* GPIO numbers and IRQ numbers are not the same. This function performs the mapping */
		rc = request_irq(irqNumber,             			// The interrupt number requested
						(irq_handler_t) gpio_irq_handler,	// The pointer to the handler function below
						IRQF_TRIGGER_RISING | IRQF_TRIGGER_FALLING, // Interrupt on either state change
						module_name,						// Used in /proc/interrupts to identify the owner
						NULL);                 				// The *dev_id for shared interrupt lines, NULL is okay
		if (rc) {
			gpio_irqcache[count] = 0;
			printk(KERN_INFO "%s: IRQ request for Port %d interrupt failed with code %d\n", module_name, count+1, rc);
		}
		else {
			gpio_irqcache[count] = irqNumber;
			printk(KERN_DEBUG "%s: Port %d is mapped to IRQ: %d\n", module_name, count+1, irqNumber);
		}
	}

	printk(KERN_DEBUG "%s: The interrupt request rc is: %d\n", module_name, rc);
	return rc;
}
 
/******************************************************************************
*   Function Name: gpiomod_exit
*   Purpose: Module unload and cleanup
*******************************************************************************/
static void __exit gpiomod_exit(void) 
{
	unsigned int count;
	for (count=0; (count < MAX_PORT_GPIOCOUNT); count++) {		
		if (gpio_irqcache[count] > 0)
			free_irq(gpio_irqcache[count], NULL);               // Free the IRQ number, no *dev_id required in this case
	}
	
	printk(KERN_DEBUG "%s: Module unloaded.\n", module_name);
}

/******************************************************************************
*   Function Name: gpiomod_sendsignal
*   Purpose: Helper function to send a signal to the user space
*******************************************************************************/
static int gpiomod_sendsignal(int val, int id, int sig)
{
    struct siginfo info;
    struct task_struct *t;
    int ret;

    ret = 0;

    if ((id > 0) && (sig > 0)) {
        memset(&info, 0, sizeof(struct siginfo));
        info.si_signo = sig;
 		
		/* Using SI_KERNEL here results in real_time data not getting delivered to the user space signal handler */
		info.si_code = SI_QUEUE;

        /* Real time signals may have 32 bits of data */
		info.si_int = val;
        info._sifields._rt._sigval.sival_int = val;
        info.si_errno = 0;

        rcu_read_lock();
        t = pid_task(find_pid_ns(id, &init_pid_ns), PIDTYPE_PID);
        if(t == NULL) {
            printk(KERN_INFO "%s: Invalid user handler PID %d\n", module_name, id);
            rcu_read_unlock();
            return -ENODEV;
        }
        ret = send_sig_info(sig, &info, t);
        rcu_read_unlock();
        
		if (ret < 0)
            printk(KERN_INFO "%s: Failed to signal with data %d to user space\n", module_name, val);
		/* else
            printk(KERN_INFO "%s: Send sig %d val %d pid %d\n", module_name, sig, val, id);
		*/
    }
    return ret;
}

/******************************************************************************
*   Function Name: gpio_irq_handler
*   Purpose: This function is the interrupt handler attached to the GPIOs 
*            defined at init. 
*******************************************************************************/ 
static irq_handler_t gpio_irq_handler(unsigned int irq, void *dev_id, struct pt_regs *regs)
{
	int count;
	int sigval;
	
	for (count=0; (count < MAX_PORT_GPIOCOUNT); count++) {	
		if ( gpio_irqcache[count] == irq )
			break;
	}

	sigval = ((count+1) & PORTID_MASK) | ((gpio_get_value(gpioid_portpresence[count]) != 0)?PORTSTATE_MASK:0);
	printk(KERN_DEBUG "%s: Port %d, siginfo %d\n", module_name, count+1, sigval);
	gpiomod_sendsignal(sigval, usrpid, sigid);
	
	return (irq_handler_t) IRQ_HANDLED;      // Announce that the IRQ has been handled correctly
}

/* The following calls are  mandatory to identify the initialization function and the cleanup functions */
module_init(gpiomod_init);
module_exit(gpiomod_exit);
