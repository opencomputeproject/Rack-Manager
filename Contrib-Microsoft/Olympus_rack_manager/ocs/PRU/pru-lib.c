// Copyright (C) Microsoft Corporation. All rights reserved.
//
// This program is free software; you can redistribute it
// and/or modify it under the terms of the GNU General Public License
// as published by the Free Software Foundation; either version 2
// of the License, or (at your option) any later version.


#include <math.h>
#include <stdlib.h>
#include <stdio.h>
#include <stdint.h>
#include <string.h>
#include <strings.h>
#include <unistd.h>
#include <signal.h>
#include <fcntl.h>
#include <sys/stat.h>
#include <sys/types.h>
#include <sys/time.h>

#include "pru-lib.h"
#include "pru-rpmsg.h"
#include "ocslog.h"
#include "ocslock.h"
#include "ocs-persist.h"

#define PRU_READ_TIMEOUT_MS 			50 	// 50 ms
#define PRU_PARTIAL_READ_TIMEOUT_MS 	5 	// 5 ms

#define PRU_SENDRECEIVE_FAILURE 		"Error in %s: SendReceive PRU failed\n"
#define SEQ_NUM_MISMATCH_ERROR 			"Error in %s: Sequence number mismatch\n"
#define PRU_SENDRECEIVE_STATUS_SUCCESS 	"%s success. \n"
#define PRU_SENDRECEIVE_STATUS_FAILURE 	"Error in %s. Command failed with status code \n"

#define QBASE_POWER						(431.6847*71.47577)
#define QBASE_VOLTAGE					431.6847
#define QBASE_CURRENT					71.47577

#define NUM_PRU_COMMANDS 				19

#if (PRU_READ_TIMEOUT_MS < PRU_PARTIAL_READ_TIMEOUT_MS*10)
        #error "PRU read timeout and PRU partial read timeout incorrectly set"
#endif

PACK(typedef struct 
{
	byte_t cmd;
	byte_t num_inputs;
	byte_t num_bytes_response; 	
	char name[32];
})prucmd_configs_t;

prucmd_configs_t prucmd_configs[NUM_PRU_COMMANDS] = 
{
	(prucmd_configs_t) {0x01, 0, 4, "GetThrottleLimit"}, 
	(prucmd_configs_t) {0x02, 1, 4, "SetThrottleLimit"},
	(prucmd_configs_t) {0x03, 0, 4, "GetPwrReading"},
	(prucmd_configs_t) {0x04, 1, 8, "GetPhasePwrReading"},
	(prucmd_configs_t) {0x05, 1, 10, "GetPhaseIReading"},
	(prucmd_configs_t) {0x06, 1, 10, "GetPhaseVReading"},
	(prucmd_configs_t) {0x08, 0, 6, "GetThrottle"},
	(prucmd_configs_t) {0x07, 2, 4, "SetThrottle"},
	(prucmd_configs_t) {0x09, 0, 4, "ControlThrottle"},
	(prucmd_configs_t) {0x0B, 2, 6, "GetOffset"},
	(prucmd_configs_t) {0x0A, 3, 4, "SetOffset"},
	(prucmd_configs_t) {0x0D, 2, 6, "GetGain"},
	(prucmd_configs_t) {0x0C, 3, 4, "SetGain"},
	(prucmd_configs_t) {0x20, 1, 4, "GetPhaseStatus"},
	(prucmd_configs_t) {0x23, 1, 4, "ClearPhaseStatus"},	
	(prucmd_configs_t) {0x21, 0, 28, "GetMaxPwrStat"},
	(prucmd_configs_t) {0x22, 0, 4, "ClearMaxPwrStat"},
	(prucmd_configs_t) {0x30, 0, 4, "GetFirmwareVersion"},
	(prucmd_configs_t) {0x31, 3, 4, "GetAdcRawData"}
};

/* 
 * Get Command number of inputs 
 * Return number of inputs >=0 when success 
 * Return -1 when command code is invalid 
 * */
const int get_command_numinputs(byte_t commandcode)
{
	int i;
	for(i = 0; i<NUM_PRU_COMMANDS; i++)
	{
		if(prucmd_configs[i].cmd == commandcode)
			return prucmd_configs[i].num_inputs;
	}	
	return -1;
}

/* 
 * Get Command number of response bytes 
 * Return >=0 when success 
 * Return -1 when command code is invalid 
 */
const int get_command_numbytes(byte_t commandcode)
{
	int i;
	for(i = 0; i<NUM_PRU_COMMANDS; i++)
	{
		if(prucmd_configs[i].cmd == commandcode)
			return prucmd_configs[i].num_bytes_response;
	}	
	return -1;
}

/* 
 * Get command code, given command name 
 * Return 0 when command name is not matched
 */
const byte_t get_command_code(char* commandname)
{
	int i;
	for(i = 0; i<NUM_PRU_COMMANDS; i++)
	{
		if(strcasecmp(prucmd_configs[i].name, commandname)==0)
			return prucmd_configs[i].cmd;
	}	
	return 0;
}

/* 
 * Get Command name 
 * Return null when command code is invalid 
 */
char* get_command_name(byte_t commandcode)
{
	int i;
	for(i = 0; i<NUM_PRU_COMMANDS; i++)
	{
		if(prucmd_configs[i].cmd == commandcode)
			return prucmd_configs[i].name;
	}	
	return NULL;
}

/*
 * Get status code string from enum int value 
 */
const char* get_statuscode(int code) 
{
   switch (code) 
   {
      case 0: return "Success";
      case 1: return "InvalidCmd";
      case 2: return "Resource";
      case 3: return "Unknown";
      default: return "UnknownStatusCode";
   }
}

/*
 *  Get measurementType string from enum int value 
 */
const char* get_measurement_type(int type) 
{
   switch (type) 
   {
      case 0: return "Current";
      case 1: return "Voltage";
      case 2: return "Power";
      default: return "UnknownMeasurementType";
   }
}

/*
 * Convert from Q14 to float
 */
double q14_to_float(unsigned int q14, measurement_t measurement)
{
	switch(measurement)
	{
		case TYPE_POWER:
			return (double) q14/(double)(pow(2,14)/QBASE_POWER);
		case TYPE_VOLTAGE:
			return (double) q14/(double)(pow(2,14)/QBASE_VOLTAGE);
		case TYPE_CURRENT:
			return (double) q14/(double)(pow(2,14)/QBASE_CURRENT);
		default:
			break;
	}
	return -1;
}

/*
 * Convert float to Q14 format
 */
unsigned int float_to_q14(float floatValue, measurement_t measurement)
{
	switch(measurement)
	{
		case TYPE_POWER:
			return (unsigned int) lround(floatValue*(double)(pow(2,14)/QBASE_POWER));
		case TYPE_VOLTAGE:
			return (unsigned int) lround(floatValue*(double)(pow(2,14)/QBASE_VOLTAGE));
		case TYPE_CURRENT:
			return (unsigned int) lround(floatValue*(double)(pow(2,14)/QBASE_CURRENT));
		default:
			break;
	}
	return 0;
}

/* 
 * Atomic increment of sequence number in file
 */ 
char seq_increment()
{
	const int MAX_SEQUENCE_NUMBER = 63;
	const char* SEQ_NUM_FILE = "/tmp/rpmsg_pru_seq_num";
	int seq_number;
	
	// If file not exists, create an empty file 
	// The only intent is to create a file, we close this file pointer after creating the file
	// Note that this block can be executed by multiple instance of this application simultaneously
	if( access( SEQ_NUM_FILE, F_OK ) == -1 ) 
	{
		mode_t org_mask = umask(0);
		int seq_handle = open(SEQ_NUM_FILE,  O_CREAT | O_RDWR | O_TRUNC | O_EXCL, (S_IRWXU | S_IRWXG | S_IRWXO));
		umask(org_mask);
		if(seq_handle < 0) {
			log_fnc_err(UNKNOWN_ERROR, "Sequence file cannot be created\n");
			return UNKNOWN_ERROR;
		}
		else
			close(seq_handle);
	}

	/* Open and Place a write lock on the file. */
	// We want to read and overwrite -- therefore use r+
	FILE* seq_ptr = fopen(SEQ_NUM_FILE, "r+");
	if(seq_ptr == NULL)
	{
		log_fnc_err(UNKNOWN_ERROR, "Sequence file cannot be opened\n");
		return UNKNOWN_ERROR;
	}

	/* Place a write lock on the file. */
	if(ocs_lock(PRU_SEQNUM)!=0)
	{
		log_fnc_err(UNKNOWN_ERROR, "Sequence file cannot be locked\n");

		/* Close the file */
		fclose(seq_ptr);

		return -1;
	}

	// Read sequence number from file.. 
	fseek( seq_ptr, 0, SEEK_SET );
	fscanf(seq_ptr, "%d ", &seq_number);
	
	// Increment the sequence number		
	if(seq_number >= MAX_SEQUENCE_NUMBER || seq_number < 0)  
		seq_number = 0; 
	else
		seq_number++;
	
	// Write incremented sequence number back to file
	fseek( seq_ptr, 0, SEEK_SET );
	fprintf(seq_ptr, "%d ", seq_number);

	/* Release the lock. */
	if(ocs_unlock(PRU_SEQNUM)!=0)
		log_fnc_err(UNKNOWN_ERROR, "Sequence file cannot be unlocked\n");
	
	// Close the file
	fclose(seq_ptr);
	
	return seq_number;
}

/*
 * Write to PRU  
 * This method is called within file lock, therefore no need for further locks
 */
int pru_write(int fd, void* sendData, int sendBytes)
{
	return write(fd, sendData, sendBytes);
}

/*
 * Read from PRU
 * This method is called within file lock, therefore no need for further locks
 * We may want to do several partial reads to accomodate slow PRU response
 */
int pru_read(int fd, void* recv_data, int recv_bytes)
{
	struct timeval stop, start;
	
	fd_set rfds;
    struct timeval tv;
    int retval;
	int num_read=0;

	/* Watch PRU file to see when it has all data to read. */
    FD_ZERO(&rfds);
    FD_SET(fd, &rfds);
	
	gettimeofday(&start, NULL);

	while(1)
	{
		/* Wait up to PRU_READ_TIMEOUT_MS  - return early if data is available */
		tv.tv_sec = 0;
		tv.tv_usec = PRU_PARTIAL_READ_TIMEOUT_MS*1000;

		/* Monitor PRU file for data availability */
		retval = select(fd+1, &rfds, NULL, NULL, &tv);
		if (retval == -1)
			log_fnc_err(UNKNOWN_ERROR, "Select call before PRU read failed\n");
		else if (retval)
			log_info("Data is available after %d microseconds.\n", PRU_PARTIAL_READ_TIMEOUT_MS*1000-tv.tv_usec);
		else
		{
			log_fnc_err(UNKNOWN_ERROR, "Entire PRU data not available after (%d) milliseconds .\n", PRU_READ_TIMEOUT_MS);
			return UNKNOWN_ERROR;
		}
		
		/* Perform PRU data file read */
		num_read += read(fd, recv_data+num_read, recv_bytes-num_read);
		
		gettimeofday(&stop, NULL);

		if(num_read >= recv_bytes)
			break;
		else
		{ 
			if(stop.tv_usec - start.tv_usec > PRU_READ_TIMEOUT_MS*1000)
			{
				log_fnc_err(UNKNOWN_ERROR, "Data unavailable after %d microseconds.\n", PRU_READ_TIMEOUT_MS*1000);
				return UNKNOWN_ERROR;
			}
		}
	}
	
	if(num_read != recv_bytes)
	{
		log_fnc_err(UNKNOWN_ERROR, "Entire PRU data could not be read (Read: %d, Expected: %d).\n", num_read, recv_bytes);
		return UNKNOWN_ERROR;
	}
	
	return num_read;
}

/*
 * Send Receive method between ARM and PRU
 * Using the rpmsg framework via /dev/rpmsg_pru* file
 * Return 0 for success, -1 (UNKNOWN_ERROR) for failure 
 */
int send_receive_pru(int send_bytes, void *send_data, int recv_bytes, void *recv_data)
{
	const char* FILENAME = "/dev/rpmsg_pru31";

	int fd = open(FILENAME, O_RDWR);
	if(fd==-1)
	{
		log_fnc_err(UNKNOWN_ERROR, "Data file cannot be accessed\n");
        return UNKNOWN_ERROR;	
	}

	/* Place a write lock on the file. */
	if(ocs_lock(PRU_CHARDEV)!=0)
	{	
		log_fnc_err(UNKNOWN_ERROR, "Data file cannot be locked\n");

		/* close the file */
		close(fd);

        	return UNKNOWN_ERROR;	
	}

	// Send Request
	if(pru_write(fd, send_data, send_bytes)!=send_bytes)
	{
		log_fnc_err(UNKNOWN_ERROR, "Send Request to PRU failed\n");

		/* Release the lock and close the file */
		ocs_unlock(PRU_CHARDEV);
		close(fd);

		return UNKNOWN_ERROR;
	}

	// Get Response
	if(pru_read(fd, recv_data, recv_bytes)!=recv_bytes)
	{	
		log_fnc_err(UNKNOWN_ERROR, "Get Response from PRU failed\n");

		/* Release the lock and close the file */
		ocs_unlock(PRU_CHARDEV);
		close(fd);

		return -1;
	}

	/* Release the lock and close the file */
	if(ocs_unlock(PRU_CHARDEV)!=0)
		log_fnc_err(UNKNOWN_ERROR, "Data file cannot be unlocked\n");
	close(fd);
	
	return 0;
}

/*
 * Get throttle limit 
 * Param1 (output): return throttle limit in watts
 * Return command success (0) or failure (!0)
 */
int get_throttle_limit(double* throttle_limit)
{
	byte_t commandcode = get_command_code("GetThrottleLimit");
	generic_t requestpacket;
	generic_t* request = &requestpacket;
	request->cmd = commandcode;
	char seqnumber = seq_increment();
	request->seq = seqnumber;
	request->status_code = 0;
	request->byte3 = 0;
	request->byte4 = 0;
		
	power_t responsepacket;
	power_t* response = &responsepacket;
	
	if(send_receive_pru(sizeof(generic_t), request, sizeof(power_t), response)!=0)
	{
		log_fnc_err(UNKNOWN_ERROR, PRU_SENDRECEIVE_FAILURE, get_command_name(commandcode));
		return -1;
	}
	
	if(response->seq != seqnumber)
	{
		log_fnc_err(UNKNOWN_ERROR, SEQ_NUM_MISMATCH_ERROR, get_command_name(commandcode));
		return -1;
	}
	
	if(response->status_code == STATUS_SUCCESS)
		log_info(PRU_SENDRECEIVE_STATUS_SUCCESS, get_command_name(commandcode));
	else
	{ 
		log_fnc_err(UNKNOWN_ERROR, PRU_SENDRECEIVE_STATUS_FAILURE, get_statuscode(response->status_code)); 
		return -1;
	}
			
	measurement_t measurement = TYPE_POWER;
	
	*throttle_limit = q14_to_float(response->power, measurement);	
	return SUCCESS;
}

/*
* Replay persisted config settings - typically done on reboot
*/
int replay_persist_config()
{
	char throttlelimit[PERSIST_VALUE_SIZE];
	if(get_persist("SetThrottleLimit", throttlelimit)!=SUCCESS)
	{
		log_fnc_err(UNKNOWN_ERROR, "Get persist value of throttle limit failed");
		return -1; 
	}
	
	if(set_throttle_limit(atof(throttlelimit))!=SUCCESS)
	{
		log_err(UNKNOWN_ERROR, "Set persist value of throttle limit failed");
		return -1;
	}
	
	char throttleenable[PERSIST_VALUE_SIZE];
	if(get_persist("SetThrottle", throttleenable)!=SUCCESS)
	{
		log_fnc_err(UNKNOWN_ERROR, "Get persist value of throttle enable failed");
		return -1; 
	}
	
	int toenablepowerlimit, toenabledcthrottle;
	sscanf(throttleenable, "%d,%d",&toenablepowerlimit, &toenabledcthrottle); 
	if(set_throttle_enable(toenablepowerlimit, toenabledcthrottle)!=SUCCESS)
	{
		log_err(UNKNOWN_ERROR, "Set persist value of throttle enable failed");
		return -1;
	}
	
	return 0;
}

/*
 * Set throttle limit
 * Param1 (input): set throttle limit in watts 
 * Return command success (0) or failure (!0)
 */
int set_throttle_limit(double limit)
{
	byte_t commandcode = get_command_code("SetThrottleLimit");
	
	if(limit < 0 || limit > (pow(2,16)-1))
	{
		log_fnc_err(UNKNOWN_ERROR, "Error: Invalid limit parameter (%f)\n", limit);
		return -1;
	}
	power_t requestpacket;
	power_t* request = &requestpacket;
	request->cmd = commandcode;
	char seqnumber = seq_increment();
	request->seq = seqnumber;
	request->status_code = 0;
	measurement_t measurement = TYPE_POWER;
	request->power = float_to_q14(limit, measurement);
	
	generic_t responsepacket; 
	generic_t* response =  &responsepacket;
	
	if(send_receive_pru(sizeof(power_t), request, sizeof(generic_t), response)!=0)
	{
		log_fnc_err(UNKNOWN_ERROR, PRU_SENDRECEIVE_FAILURE, get_command_name(commandcode));
		return -1;
	}

	if(response->seq != seqnumber)
	{
		log_fnc_err(UNKNOWN_ERROR, SEQ_NUM_MISMATCH_ERROR, get_command_name(commandcode));
		return -1;
	}
	
	if(response->status_code == STATUS_SUCCESS)
		log_info(PRU_SENDRECEIVE_STATUS_SUCCESS, get_command_name(commandcode));
	else 
	{ 
		log_fnc_err(UNKNOWN_ERROR, PRU_SENDRECEIVE_STATUS_FAILURE, get_statuscode(response->status_code)); 
		return -1;
	}
	
	char persist_value[PERSIST_VALUE_SIZE];
	snprintf(persist_value, PERSIST_VALUE_SIZE, "%f", limit);
	if(set_persist("SetThrottleLimit", persist_value)!=SUCCESS)
	{
		log_fnc_err(UNKNOWN_ERROR, "Persist of set throttle limit(%s) failed", persist_value);
		return -1; 
	}
		
	return 0;
}

/*
 * Get power
 * Param1 (output): power in watts 
 * Return command success (0) or failure (!0)
 */
int get_power(double* power)
{
	byte_t commandcode = get_command_code("GetPwrReading");
	generic_t requestpacket;
	generic_t* request = &requestpacket;
	request->cmd = commandcode;
	char seqnumber = seq_increment();
	request->seq = seqnumber;
	request->status_code = 0;
	request->byte3 = 0;
	request->byte4 = 0;
	power_t responsepacket;
	power_t* response = &responsepacket; 

	if(send_receive_pru(sizeof(generic_t), request, sizeof(power_t), response)!=0)
	{
		log_fnc_err(UNKNOWN_ERROR, PRU_SENDRECEIVE_FAILURE, get_command_name(commandcode));
		return -1;
	}
	
	if(response->seq != seqnumber)
	{
		log_fnc_err(UNKNOWN_ERROR, SEQ_NUM_MISMATCH_ERROR, get_command_name(commandcode));
		return -1;
	}
	
	if(response->status_code == STATUS_SUCCESS)
		log_info(PRU_SENDRECEIVE_STATUS_SUCCESS, get_command_name(commandcode));
	else 
	{ 
		log_fnc_err(UNKNOWN_ERROR, PRU_SENDRECEIVE_STATUS_FAILURE, get_statuscode(response->status_code)); 
		return -1;
	}
		
	measurement_t measurement = TYPE_POWER;			
	*power = q14_to_float(response->power, measurement);
	
	return SUCCESS;
}

/*
 * Enable or Disable throttle
 * Param1: toenablepowerlimit: 1 (enable), 0 (disable) 
 * Param1: toenabledcthrottle: 1 (enable), 0 (disable) 
 */
int set_throttle_enable(int toenablepowerlimit, int toenabledcthrottle)
{
	byte_t commandcode = get_command_code("SetThrottle");
	
	if(toenablepowerlimit!=0 && toenablepowerlimit!=1)
	{
		log_fnc_err(UNKNOWN_ERROR,"Error: %s Invalid input parameter, toenablepowerlimit:(%d) is neither 0 nor 1\n", get_command_name(commandcode), toenablepowerlimit);
		return -1;
	}
	if(toenabledcthrottle!=0 && toenabledcthrottle!=1)
	{
		log_fnc_err(UNKNOWN_ERROR,"Error: %s Invalid input parameter, toenabledcthrottle:(%d) is neither 0 nor 1\n", get_command_name(commandcode), toenabledcthrottle);
		return -1;
	}
	generic_t requestpacket;
	generic_t* request = &requestpacket;
	request->cmd = commandcode;
	char seqnumber = seq_increment();
	request->seq = seqnumber;
	request->status_code = 0;
	request->byte3 = toenablepowerlimit;
	request->byte4 = toenabledcthrottle;
	
	generic_t responsepacket; 
	generic_t* response = &responsepacket;
	
	if(send_receive_pru(sizeof(generic_t), request, sizeof(generic_t), response)!=0)
	{
		log_fnc_err(UNKNOWN_ERROR,PRU_SENDRECEIVE_FAILURE, get_command_name(commandcode));
		return -1;
	}
	
	if(response->seq != seqnumber)
	{
		log_fnc_err(UNKNOWN_ERROR,SEQ_NUM_MISMATCH_ERROR, get_command_name(commandcode));
		return -1;
	}
	
	if(response->status_code == STATUS_SUCCESS)
		log_info(PRU_SENDRECEIVE_STATUS_SUCCESS, get_command_name(commandcode));
	else 
	{ 
		log_fnc_err(UNKNOWN_ERROR,PRU_SENDRECEIVE_STATUS_FAILURE, get_statuscode(response->status_code)); 
		return -1;
	}			
	
	char persist_value[PERSIST_VALUE_SIZE];
	snprintf(persist_value, PERSIST_VALUE_SIZE, "%d,%d", toenablepowerlimit, toenabledcthrottle);
	if(set_persist("SetThrottle", persist_value)!=SUCCESS)
	{
		log_fnc_err(UNKNOWN_ERROR, "Persist of set throttle enable `(%s) failed", persist_value);
		return -1; 
	}
	
	return 0;
}

/*
 * Get throttle status:
 * 		powerlimit enabled? 
 * 	 	powerlimit active?
 * 		dcthrottle enabled? 
 * 		dcthrottle active? 
 */
int get_throttle_status(int* powerlimit_enable, int* powerlimit_active, int* dcthrottle_enable, int* dcthrottle_active)
{
	byte_t commandcode = get_command_code("GetThrottle");
	generic_t requestpacket; 
	generic_t* request = &requestpacket; 
	request->cmd = commandcode;
	char seqnumber = seq_increment();
	request->seq = seqnumber;
	request->status_code = 0;
	request->byte3 = 0;
	request->byte4 = 0;
	
	throttle_t responsepacket; 
	throttle_t* response = &responsepacket; 
	
	if(send_receive_pru(sizeof(generic_t), request, sizeof(throttle_t), response)!=0)
	{
		log_fnc_err(UNKNOWN_ERROR, PRU_SENDRECEIVE_FAILURE, get_command_name(commandcode));
		return -1;
	}
	
	if(response->seq != seqnumber)
	{
		log_fnc_err(UNKNOWN_ERROR, SEQ_NUM_MISMATCH_ERROR, get_command_name(commandcode));
		return -1;
	}
	
	if(response->status_code == STATUS_SUCCESS)
		log_info(PRU_SENDRECEIVE_STATUS_SUCCESS, get_command_name(commandcode));
	else 
	{ 
		log_fnc_err(UNKNOWN_ERROR, PRU_SENDRECEIVE_STATUS_FAILURE, get_statuscode(response->status_code)); 
		return -1;
	}			
			
	if(response->powerlimit_enable == 0 || response->powerlimit_enable == 1)
	{
		*powerlimit_enable = response->powerlimit_enable;
	}
	else 
		log_info("Is power limit Throttle Enabled: Error, Could not be determined. \n");
	
	if(response->powerlimit_active== 0 || response->powerlimit_active== 1)
	{
		*powerlimit_active = response->powerlimit_active;
	}
	else 
		log_info("Current Powerlimit Throttle State: Error, Could not be determined. \n");

        if(response->dcthrottle_enable == 0 || response->dcthrottle_enable == 1)
        {
                *dcthrottle_enable = response->dcthrottle_enable;
        }
        else
                log_info("Is DcThrottle Enabled: Error, Could not be determined. \n");

        if(response->dcthrottle_active== 0 || response->dcthrottle_active== 1)
        {
                // dcthrottle is active low - make inversion 
                *dcthrottle_active = (response->dcthrottle_active==1) ? 0 : 1;
        }
        else
                log_info("Current DcThrottle State: Error, Could not be determined. \n");
	
	return SUCCESS;
}

/*
 * Assert or de-assert throttle 
 */
int set_throttle_active(int toassert)
{
	byte_t commandcode = get_command_code("ControlThrottle");
	if(toassert!=0 && toassert!=1)
	{
		log_fnc_err(UNKNOWN_ERROR,"Error: %s Invalid input parameter, toassert:(%d) is neither 0 nor 1\n", get_command_name(commandcode), toassert);
		return -1;
	}
	generic_t requestpacket;
	generic_t* request = &requestpacket; 
	request->cmd = commandcode;
	char seqnumber = seq_increment();
	request->seq = seqnumber;
	request->status_code = 0;
	request->byte3 = toassert;
	request->byte4 = 0;
	
	generic_t responsepacket; 
	generic_t* response = &responsepacket; 
	
	if(send_receive_pru(sizeof(generic_t), request, sizeof(generic_t), response)!=0)
	{
		log_fnc_err(UNKNOWN_ERROR, PRU_SENDRECEIVE_FAILURE, get_command_name(commandcode));
		return FAILURE;
	}
	
	if(response->seq != seqnumber)
	{
		log_fnc_err(UNKNOWN_ERROR, SEQ_NUM_MISMATCH_ERROR, get_command_name(commandcode));
		return FAILURE;
	}
	
	if(response->status_code == STATUS_SUCCESS)
		log_info(PRU_SENDRECEIVE_STATUS_SUCCESS, get_command_name(commandcode));
	else 
	{ 
		log_fnc_err(UNKNOWN_ERROR, PRU_SENDRECEIVE_STATUS_FAILURE, get_statuscode(response->status_code)); 
		return FAILURE;
	}			

	return SUCCESS;
}

/*
 * Set calibration offset
 * Param1: phase 1 to 6
 * Param2: current (0) or voltage (1)
 * Param3: offset value
 */
int set_offset(int phase, int currentorvoltage, int value)
{
	byte_t commandcode = get_command_code("SetOffset");
	
	if(phase<1 || phase >6)
	{
		log_fnc_err(UNKNOWN_ERROR, "Error: %s Invalid input parameter, phase:(%d) is not between 1-6 \n", get_command_name(commandcode), phase);
		return -1;
	}
	if(currentorvoltage!=0 && currentorvoltage!=1)
	{
		log_fnc_err(UNKNOWN_ERROR, "Error: %s Invalid input parameter, currentOrVoltage choice:(%d) is neither 1 (V) nor 0 (I) \n", get_command_name(commandcode), currentorvoltage);
		return -1;
	}
	if(value < 0 || value >= 256*256)
	{
		log_fnc_err(UNKNOWN_ERROR, "Error: %s Invalid input parameter, value (%d) is not between 0 and 2^16 \n", get_command_name(commandcode), value);
		return -1;
	}
	
	calibration_t requestpacket; 
	calibration_t* request = &requestpacket;
	request->cmd = commandcode;
	char seqnumber = seq_increment();
	request->seq = seqnumber;
	request->status_code = 0;
	request->phase = phase;
	request->currentorvoltage = currentorvoltage;
	request->value = value; /* We will be getting Offset in Q14 format, so no need for conversion */
	
	generic_t responsepacket;
	generic_t* response = &responsepacket; 
	
	if(send_receive_pru(sizeof(calibration_t), request, sizeof(generic_t), response)!=0)
	{
		log_fnc_err(UNKNOWN_ERROR, PRU_SENDRECEIVE_FAILURE, get_command_name(commandcode));
		return -1;
	}
	
	if(response->seq != seqnumber)
	{
		log_fnc_err(UNKNOWN_ERROR, SEQ_NUM_MISMATCH_ERROR, get_command_name(commandcode));
		return -1;
	}
	
	if(response->status_code == STATUS_SUCCESS)
		log_info(PRU_SENDRECEIVE_STATUS_SUCCESS, get_command_name(commandcode));
	else 
	{ 
		log_fnc_err(UNKNOWN_ERROR, PRU_SENDRECEIVE_STATUS_FAILURE, get_statuscode(response->status_code)); 
		return -1;
	}			
	
	return 0;
}

/*
 * Get calibration offset
 * Param1: phase 1 to 6
 * Param2: current (0) or voltage (1)
 * Param3 (output): offset value
 */
int get_offset(int phase, int currentorvoltage, int* value)
{
	byte_t commandcode = get_command_code("GetOffset");
	
	if(phase<1 || phase >6)
	{
		log_fnc_err(UNKNOWN_ERROR, "Error: %s Invalid input parameter, phase:(%d) is not between 1-6 \n", get_command_name(commandcode), phase);
		return -1;
	}
	if(currentorvoltage!=0 && currentorvoltage!=1)
	{
		log_fnc_err(UNKNOWN_ERROR, "Error: %s Invalid input parameter, currentOrVoltage choice:(%d) is neither 1 (V) nor 0 (I) \n", get_command_name(commandcode), currentorvoltage);
		return -1;
	}
	generic_t requestpacket;
	generic_t* request = &requestpacket;
	request->cmd = commandcode;
	char seqnumber = seq_increment();
	request->seq = seqnumber;
	request->status_code = 0;
	request->byte3 = phase;
	request->byte4 = currentorvoltage;
	
	calibration_t responsepacket;
	calibration_t* response = &responsepacket; 
	
	if(send_receive_pru(sizeof(generic_t), request, sizeof(calibration_t), response)!=0)
	{
		log_fnc_err(UNKNOWN_ERROR, PRU_SENDRECEIVE_FAILURE, get_command_name(commandcode));
		return -1;
	}
	
	if(response->seq != seqnumber)
	{
		log_fnc_err(UNKNOWN_ERROR, SEQ_NUM_MISMATCH_ERROR, get_command_name(commandcode));
		return -1;
	}
	
	if(response->status_code == STATUS_SUCCESS)
		log_info(PRU_SENDRECEIVE_STATUS_SUCCESS, get_command_name(commandcode));
	else 
	{ 
		log_fnc_err(UNKNOWN_ERROR, PRU_SENDRECEIVE_STATUS_FAILURE, get_statuscode(response->status_code)); 
		return -1;
	}
	
	if(response->phase<1 || response->phase>6)
		log_info("Warning in %s: Phase/Feed value is invalid\n", get_command_name(commandcode));
	if(response->currentorvoltage!=0 && response->currentorvoltage!=1)
		log_info("Warning in %s: Current Or Voltage response is invalid\n", get_command_name(commandcode));
		 
	*value = response->value;
	
	return SUCCESS;
}

/*
 * Set calibration gain
 * Param1: phase 1 to 6
 * Param2: current (0) or voltage (1)
 * Param3: gain value
 */
int set_gain(int phase, int currentorvoltage, int value)
{
	byte_t commandcode = get_command_code("SetGain");

	if(phase<1 || phase >6)
	{
		log_fnc_err(UNKNOWN_ERROR, "Error: %s Invalid input parameter, phase:(%d) is not between 1-6 \n", get_command_name(commandcode), phase);
		return -1;
	}
	if(currentorvoltage!=0 && currentorvoltage!=1)
	{
		log_fnc_err(UNKNOWN_ERROR, "Error: %s Invalid input parameter, currentOrVoltage choice:(%d) is neither 1 (V) nor 0 (I) \n", get_command_name(commandcode), currentorvoltage);
		return -1;
	}
	if(value < 0 || value > 256*256)
	{
		log_fnc_err(UNKNOWN_ERROR, "Error: %s Invalid input parameter, value (%d) is not between 0 and 2^16 \n", get_command_name(commandcode), value);
		return -1;
	}
	
	calibration_t requestpacket; 
	calibration_t* request = &requestpacket;
	request->cmd = commandcode;
	char seqnumber = seq_increment();
	request->seq = seqnumber;
	request->status_code = 0;
	request->phase = phase;
	request->currentorvoltage = currentorvoltage;
	request->value = value; // We will be getting Gain in Q14 format, so no need for conversion  
	
	generic_t responsepacket; 
	generic_t* response = &responsepacket; 
	
	if(send_receive_pru(sizeof(calibration_t), request, sizeof(generic_t), response)!=0)
	{
		log_fnc_err(UNKNOWN_ERROR, PRU_SENDRECEIVE_FAILURE, get_command_name(commandcode));
		return -1;
	}
	
	if(response->seq != seqnumber)
	{
		log_fnc_err(UNKNOWN_ERROR, SEQ_NUM_MISMATCH_ERROR, get_command_name(commandcode));
		return -1;
	}
	
	if(response->status_code == STATUS_SUCCESS)
		log_info(PRU_SENDRECEIVE_STATUS_SUCCESS, get_command_name(commandcode));
	else 
	{ 
		log_fnc_err(UNKNOWN_ERROR, PRU_SENDRECEIVE_STATUS_FAILURE, get_statuscode(response->status_code)); 
		return -1;
	}
	
	return 0;
}

/*
 * Get calibration gain
 * Param1: phase 1 to 6
 * Param2: current (0) or voltage (1)
 * Param3 (output): offset value
 */
int get_gain(int phase, int currentorvoltage, int* value)
{
	byte_t commandcode = get_command_code("GetGain");
	
	if(phase<1 || phase >6)
	{
		log_fnc_err(UNKNOWN_ERROR, "Error: %s Invalid input parameter, phase:(%d) is not between 1-6 \n", get_command_name(commandcode), phase);
		return -1;
	}
	if(currentorvoltage!=0 && currentorvoltage!=1)
	{
		log_fnc_err(UNKNOWN_ERROR, "Error: %s Invalid input parameter, currentOrVoltage choice:(%d) is neither 1 (V) nor 0 (I) \n", get_command_name(commandcode), currentorvoltage);
		return -1;
	}
	
	generic_t requestpacket;
	generic_t* request = &requestpacket; 
	request->cmd = commandcode;
	char seqnumber = seq_increment();
	request->seq = seqnumber;	
	request->status_code = 0;
	request->byte3 = phase;
	request->byte4 = currentorvoltage;
	
	calibration_t responsepacket;
	calibration_t* response = &responsepacket; 
	
	if(send_receive_pru(sizeof(generic_t), request, sizeof(calibration_t), response)!=0)
	{
		log_fnc_err(UNKNOWN_ERROR, PRU_SENDRECEIVE_FAILURE, get_command_name(commandcode));
		return -1;
	}
	
	if(response->seq != seqnumber)
	{
		log_fnc_err(UNKNOWN_ERROR, SEQ_NUM_MISMATCH_ERROR, get_command_name(commandcode));
		return -1;
	}
	
	if(response->status_code == STATUS_SUCCESS)
		log_info(PRU_SENDRECEIVE_STATUS_SUCCESS, get_command_name(commandcode));
	else 
	{ 
		log_fnc_err(UNKNOWN_ERROR, PRU_SENDRECEIVE_STATUS_FAILURE, get_statuscode(response->status_code)); 
		return -1;
	}

	if(response->phase<1 || response->phase>6)
		log_info("Warning in %s: Phase/Feed value is invalid\n", get_command_name(commandcode));
	if(response->currentorvoltage!=0 && response->currentorvoltage!=1)
		log_info("Warning in %s: Current Or Voltage response is invalid\n", get_command_name(commandcode));
		 
	*value = response->value;

	return 0;
}

/*
 * Get phase power reading for given feed
 * Return command success (0) or failure (!0)
 */
int get_phase_power(int feed, phase_val_t* phase_val)
{
	byte_t commandcode = get_command_code("GetPhasePwrReading");
	if(feed!=0 && feed!=1)
	{
		log_fnc_err(UNKNOWN_ERROR, "Error: %s Invalid input parameter, feed:(%d) is neither 0(A) nor 1(B)\n", get_command_name(commandcode), feed);
		return -1;
	}
	generic_t requestpacket;
	generic_t* request = &requestpacket;
	request->cmd = commandcode;
	char seqnumber = seq_increment();
	request->seq = seqnumber;
	request->status_code = 0;
	request->byte3 = feed;
	request->byte4 = 0;
	
	power_phase_t responsepacket;
	power_phase_t* response = &responsepacket; 
	
	if(send_receive_pru(sizeof(generic_t), request, sizeof(power_phase_t), response)!=0)
	{
		log_fnc_err(UNKNOWN_ERROR, PRU_SENDRECEIVE_FAILURE, get_command_name(commandcode));
		return -1;
	}
	
	if(response->seq != seqnumber)
	{
		log_fnc_err(UNKNOWN_ERROR, SEQ_NUM_MISMATCH_ERROR, get_command_name(commandcode));
		return -1;
	}
	
	if(response->status_code == STATUS_SUCCESS)
		log_info(PRU_SENDRECEIVE_STATUS_SUCCESS, get_command_name(commandcode));
	else 
	{ 
		log_fnc_err(UNKNOWN_ERROR, PRU_SENDRECEIVE_STATUS_FAILURE, get_statuscode(response->status_code)); 
		return -1;
	}			
	
	measurement_t measurement = TYPE_POWER;
	(*phase_val).phase1_val = q14_to_float(response->phase1_pwr, measurement);
	(*phase_val).phase2_val = q14_to_float(response->phase2_pwr, measurement);
	(*phase_val).phase3_val = q14_to_float(response->phase3_pwr, measurement);
	
	return SUCCESS;
}

/*
 * Get phase voltage reading for given feed
 * Return command success (0) or failure (!0)
 */
int get_phase_voltage(int feed, phase_val_t* phase_val)
{
	byte_t commandcode = get_command_code("GetPhaseVReading");
	if(feed!=0 && feed!=1)
	{
		log_fnc_err(UNKNOWN_ERROR, "Error: %s Invalid input parameter, feed:(%d) is neither 0(A) nor 1(B)\n", get_command_name(commandcode), feed);
		return -1;
	}
	generic_t requestpacket;
	generic_t* request = &requestpacket; 
	request->cmd = commandcode;
	char seqnumber = seq_increment();
	request->seq = seqnumber;
	request->status_code = 0;
	request->byte3 = feed;
	request->byte4 = 0;
	
	curr_volt_t responsepacket;
	curr_volt_t* response = &responsepacket; 
	
	if(send_receive_pru(sizeof(generic_t), request, sizeof(curr_volt_t), response)!=0)
	{
		log_fnc_err(UNKNOWN_ERROR, PRU_SENDRECEIVE_FAILURE, get_command_name(commandcode));
		return -1;
	}
	
	if(response->seq != seqnumber)
	{
		log_fnc_err(UNKNOWN_ERROR, SEQ_NUM_MISMATCH_ERROR, get_command_name(commandcode));
		return -1;
	}
	
	if(response->status_code == STATUS_SUCCESS)
		log_info(PRU_SENDRECEIVE_STATUS_SUCCESS, get_command_name(commandcode));
	else 
	{ 
		log_fnc_err(UNKNOWN_ERROR, PRU_SENDRECEIVE_STATUS_FAILURE, get_statuscode(response->status_code)); 
		return -1;
	}
	
	if(response->feed!=0 && response->feed!=1)
		log_info("Warning in %s: feed value (%d) is invalid.\n", get_command_name(commandcode), response->feed);
	
	measurement_t measurement = TYPE_VOLTAGE;	
	(*phase_val).phase1_val = q14_to_float(response->phase1, measurement);
	(*phase_val).phase2_val = q14_to_float(response->phase2, measurement);
	(*phase_val).phase3_val = q14_to_float(response->phase3, measurement);
	
	return SUCCESS;
}

/*
 * Get phase voltage reading for given feed
 * Return command success (0) or failure (!0)
 */
int get_phase_current(int feed, phase_val_t* phase_val)
{
	byte_t commandcode = get_command_code("GetPhaseIReading");
	if(feed!=0 && feed!=1)
	{
		log_fnc_err(UNKNOWN_ERROR, "Error: %s Invalid input parameter, feed:(%d) is neither 0(A) nor 1(B)\n", get_command_name(commandcode), feed);
		return -1;
	}
	
	generic_t requestpacket;
	generic_t* request = &requestpacket;
	request->cmd = commandcode;
	char seqnumber = seq_increment();
	request->seq = seqnumber;
	request->status_code = 0;
	request->byte3 = feed;
	request->byte4 = 0;
	
	curr_volt_t responsepacket;
	curr_volt_t* response = &responsepacket;
	
	if(send_receive_pru(sizeof(generic_t), request, sizeof(curr_volt_t), response)!=0)
	{
		log_fnc_err(UNKNOWN_ERROR, PRU_SENDRECEIVE_FAILURE, get_command_name(commandcode));
		return -1;
	}
	
	if(response->seq != seqnumber)
	{
		log_fnc_err(UNKNOWN_ERROR, SEQ_NUM_MISMATCH_ERROR, get_command_name(commandcode));
		return -1;
	}
	
	if(response->status_code == STATUS_SUCCESS)
		log_info(PRU_SENDRECEIVE_STATUS_SUCCESS, get_command_name(commandcode));
	else 
	{ 
		log_fnc_err(UNKNOWN_ERROR, PRU_SENDRECEIVE_STATUS_FAILURE, get_statuscode(response->status_code)); 
		return -1;
	}
	
	if(response->feed!=0 && response->feed!=1)
		log_info("Warning in %s: feed value (%d) is invalid.\n", get_command_name(commandcode), response->feed);
	
	measurement_t measurement = TYPE_CURRENT;	
	(*phase_val).phase1_val = q14_to_float(response->phase1, measurement);
	(*phase_val).phase2_val = q14_to_float(response->phase2, measurement);
	(*phase_val).phase3_val = q14_to_float(response->phase3, measurement);
		
	return SUCCESS;
}

/*
 * Clear phase status
 */
int clear_phase_status(int feed)
{
	byte_t commandcode = get_command_code("ClearPhaseStatus");
	if(feed!=0 && feed!=1)
	{
		log_fnc_err(UNKNOWN_ERROR, "Error: %s Invalid input parameter, feed:(%d) is neither 0(A) nor 1(B)\n", get_command_name(commandcode), feed);
		return -1;
	}
	generic_t requestpacket;
	generic_t* request = &requestpacket; 
	request->cmd = commandcode;
	char seqnumber = seq_increment();
	request->seq = seqnumber;
	request->status_code = 0;
	request->byte3 = feed;
	request->byte4 = 0;
	
	feed_status_t responsepacket;
	feed_status_t* response = &responsepacket; 
	
	if(send_receive_pru(sizeof(generic_t), request, sizeof(feed_status_t), response)!=0)
	{
		log_fnc_err(UNKNOWN_ERROR, PRU_SENDRECEIVE_FAILURE, get_command_name(commandcode));
		return -1;
	}
	
	if(response->seq != seqnumber)
	{
		log_fnc_err(UNKNOWN_ERROR, SEQ_NUM_MISMATCH_ERROR, get_command_name(commandcode));
		return -1;
	}
	
	if(response->status_code == STATUS_SUCCESS)
		log_info(PRU_SENDRECEIVE_STATUS_SUCCESS, get_command_name(commandcode));
	else 
	{ 
		log_fnc_err(UNKNOWN_ERROR, PRU_SENDRECEIVE_STATUS_FAILURE, get_statuscode(response->status_code)); 
		return -1;
	}

	return SUCCESS;
}

/* 
 * Get status of all phases
 * Param1: Feed (0 or 1)
 */
int get_phase_status(int feed, feed_power_status_t* feed_status)
{
	byte_t commandcode = get_command_code("GetPhaseStatus");
	if(feed!=0 && feed!=1)
	{
		log_fnc_err(UNKNOWN_ERROR, "Error: %s Invalid input parameter, feed:(%d) is neither 0(A) nor 1(B)\n", get_command_name(commandcode), feed);
		return -1;
	}
	
	generic_t requestpacket;
	generic_t* request = &requestpacket; 
	request->cmd = commandcode;
	char seqnumber = seq_increment();
	request->seq = seqnumber;
	request->status_code = 0;
	request->byte3 = feed;
	request->byte4 = 0;
	
	feed_status_t responsepacket;
	feed_status_t* response = &responsepacket; 
	
	if(send_receive_pru(sizeof(generic_t), request, sizeof(feed_status_t), response)!=0)
	{
		log_fnc_err(UNKNOWN_ERROR, PRU_SENDRECEIVE_FAILURE, get_command_name(commandcode));
		return -1;
	}
	
	if(response->seq != seqnumber)
	{
		log_fnc_err(UNKNOWN_ERROR, SEQ_NUM_MISMATCH_ERROR, get_command_name(commandcode));
		return -1;
	}
	
	if(response->status_code == STATUS_SUCCESS)
		log_info(PRU_SENDRECEIVE_STATUS_SUCCESS, get_command_name(commandcode));
	else 
	{ 
		log_fnc_err(UNKNOWN_ERROR, PRU_SENDRECEIVE_STATUS_FAILURE, get_statuscode(response->status_code)); 
		return -1;
	}
	
	feed_status->power_negated = response->power_negated;
	feed_status->oc_throttle_limit = response->oc_throttle_limit;
	feed_status->logic_error = response->logic_error;
	feed_status->unknown_fault = response->unknown_fault;
	feed_status->phase1_V_OV_fault = response->phase1_V_OV_fault;
	feed_status->phase1_V_UV_fault = response->phase1_V_UV_fault;
	feed_status->phase1_I_OC_fault = response->phase1_I_OC_fault;
	
	feed_status->phase2_V_OV_fault = response->phase2_V_OV_fault;
	feed_status->phase2_V_UV_fault = response->phase2_V_UV_fault;
	feed_status->phase2_I_OC_fault = response->phase2_I_OC_fault;
	
	feed_status->phase3_V_OV_fault = response->phase3_V_OV_fault;
	feed_status->phase3_V_UV_fault = response->phase3_V_UV_fault;
	feed_status->phase3_I_OC_fault = response->phase3_I_OC_fault;
	
	return SUCCESS;
}

/*
 * Get MAX power statistics
 */
int get_max_power(max_power_stat_t* power_stat)
{
	byte_t commandcode = get_command_code("GetMaxPwrStat");
	generic_t requestpacket;
	generic_t* request = &requestpacket; 
	request->cmd = commandcode;
	char seqnumber = seq_increment();
	request->seq = seqnumber;
	request->status_code = 0;
	request->byte3 = 0;
	request->byte4 = 0;
	
	max_power_t responsepacket;
	max_power_t* response = &responsepacket; 
	
	if(send_receive_pru(sizeof(generic_t), request, sizeof(max_power_t), response)!=0)
	{
		log_fnc_err(UNKNOWN_ERROR, PRU_SENDRECEIVE_FAILURE, get_command_name(commandcode));
		return -1;
	}
	
	if(response->seq != seqnumber)
	{
		log_fnc_err(UNKNOWN_ERROR, SEQ_NUM_MISMATCH_ERROR, get_command_name(commandcode));
		return -1;
	}
	
	if(response->status_code == STATUS_SUCCESS)
		log_info(PRU_SENDRECEIVE_STATUS_SUCCESS, get_command_name(commandcode));
	else 
	{ 
		log_fnc_err(UNKNOWN_ERROR, PRU_SENDRECEIVE_STATUS_FAILURE, get_statuscode(response->status_code)); 
		return -1;
	}
	
	(*power_stat).pwr = q14_to_float(response->pwr, TYPE_POWER);	

	(*power_stat).feed1_phase1_amps = q14_to_float(response->feed1_phase1_amps, TYPE_CURRENT);	
	(*power_stat).feed1_phase2_amps = q14_to_float(response->feed1_phase2_amps, TYPE_CURRENT); 
	(*power_stat).feed1_phase3_amps = q14_to_float(response->feed1_phase3_amps, TYPE_CURRENT);

	(*power_stat).feed1_phase1_volts = q14_to_float(response->feed1_phase1_volts, TYPE_VOLTAGE);	
	(*power_stat).feed1_phase2_volts = q14_to_float(response->feed1_phase2_volts, TYPE_VOLTAGE); 
	(*power_stat).feed1_phase3_volts = q14_to_float(response->feed1_phase3_volts, TYPE_VOLTAGE);

	(*power_stat).feed2_phase1_amps = q14_to_float(response->feed2_phase1_amps, TYPE_CURRENT);
	(*power_stat).feed2_phase2_amps = q14_to_float(response->feed2_phase2_amps, TYPE_CURRENT);
	(*power_stat).feed2_phase3_amps = q14_to_float(response->feed2_phase3_amps, TYPE_CURRENT);
	
	(*power_stat).feed2_phase1_volts = q14_to_float(response->feed2_phase1_volts, TYPE_VOLTAGE);
	(*power_stat).feed2_phase2_volts = q14_to_float(response->feed2_phase2_volts, TYPE_VOLTAGE);
	(*power_stat).feed2_phase3_volts = q14_to_float(response->feed2_phase3_volts, TYPE_VOLTAGE);
		
	return SUCCESS;
}

/*
 * Clear max power
 */
int clear_max_power()
{
	byte_t commandcode = get_command_code("ClearMaxPwrStat");
	generic_t requestpacket; 
	generic_t* request = &requestpacket; 
	request->cmd = commandcode;
	char seqnumber = seq_increment();
	request->seq = seqnumber;
	request->status_code = 0;
	request->byte3 = 0;
	request->byte4 = 0;
	
	generic_t responsepacket; 
	generic_t* response = &responsepacket; 
	
	if(send_receive_pru(sizeof(generic_t), request, sizeof(generic_t), response)!=0)
	{
		log_fnc_err(UNKNOWN_ERROR, PRU_SENDRECEIVE_FAILURE, get_command_name(commandcode));
		return -1;
	}
	
	if(response->seq != seqnumber)
	{
		log_fnc_err(UNKNOWN_ERROR, SEQ_NUM_MISMATCH_ERROR, get_command_name(commandcode));
		return -1;
	}
	
	if(response->status_code == STATUS_SUCCESS)
		log_info(PRU_SENDRECEIVE_STATUS_SUCCESS, get_command_name(commandcode));
	else 
	{ 
		log_fnc_err(UNKNOWN_ERROR, PRU_SENDRECEIVE_STATUS_FAILURE, get_statuscode(response->status_code)); 
		return -1;
	}
	
	return 0;
}

/*
 * Get PRU fw version 
 */
int get_pru_fw_version(int* major_version, int* minor_version)
{
	byte_t commandcode = get_command_code("GetFirmwareVersion");
	generic_t requestpacket;
	generic_t* request = &requestpacket; 
	request->cmd = commandcode;
	char seqnumber = seq_increment();
	request->seq = seqnumber;
	request->status_code = 0;
	request->byte3 = 0;
	request->byte4 = 0;
	
	generic_t responsepacket;
	generic_t* response = &responsepacket; 
	
	if(send_receive_pru(sizeof(generic_t), request, sizeof(generic_t), response)!=0)
	{
		log_fnc_err(UNKNOWN_ERROR, PRU_SENDRECEIVE_FAILURE, get_command_name(commandcode));
		return -1;
	}
	
	if(response->seq != seqnumber)
	{
		log_fnc_err(UNKNOWN_ERROR, SEQ_NUM_MISMATCH_ERROR, get_command_name(commandcode));
		return -1;
	}
	
	if(response->status_code == STATUS_SUCCESS)
		log_info(PRU_SENDRECEIVE_STATUS_SUCCESS, get_command_name(commandcode));
	else 
	{ 
		log_fnc_err(UNKNOWN_ERROR, PRU_SENDRECEIVE_STATUS_FAILURE, get_statuscode(response->status_code)); 
		return -1;
	}
	
	*major_version = response->byte4;
	*minor_version = response->byte3;
	
	return 0;
}

/*
 * Get ADC raw data - COMMAND NOT IMPLEMENTED CURRENTLY
 */
//int GetAdcRawData(char* input1, char* input2, char* input3)
//{
	//byte_t commandcode = get_command_code("GetAdcRawData");
	//int numsamples = atoi(input1);
	//int adcnumber = atoi(input2);
	//int channel = atoi(input3);
	//const int numbytespersample = 2; // Hard coded to work around the PRU device file read() bug
	//if(numsamples < 0 || numsamples > MAX_ADC_RAW_BYTES)
	//{
		//log_fnc_err(UNKNOWN_ERROR, "Error: %s Invalid input parameter, number of samples(%d)\n", get_command_name(commandcode), numsamples);
		//return -1;
	//}
	//if(adcnumber!=0 && adcnumber!=1)
	//{
		//log_fnc_err(UNKNOWN_ERROR, "Error: %s Invalid input parameter, adcnumber:(%d) is neither 0 nor 1\n", get_command_name(commandcode), adcnumber);
		//return -1;
	//}
	//if(channel<1 || channel >6)
	//{
		//log_fnc_err(UNKNOWN_ERROR, "Error: %s Invalid input parameter, channel:(%d) is not between 1-6 \n", get_command_name(commandcode), channel);
		//return -1;
	//}
	
	//adc_request_t requestpacket;
	//adc_request_t* request = &requestpacket; 
	//request->cmd = commandcode;
	//char seqnumber = seq_increment();
	//request->seq = seqnumber;
	//request->status_code = 0;
	//request->numsamples = numsamples; 
	//request->adcnumber = adcnumber;
	//request->channel = channel;

	//adc_response_t responsepacket; 
	//adc_response_t* response = &responsepacket; 

	//if(send_receive_pru(sizeof(adc_request_t), request, sizeof(adc_response_t), response)!=0)
	//{
		//log_fnc_err(UNKNOWN_ERROR, PRU_SENDRECEIVE_FAILURE, get_command_name(commandcode));
		//return -1;
	//}

	//if(response->seq != seqnumber)
	//{
		//log_fnc_err(UNKNOWN_ERROR, SEQ_NUM_MISMATCH_ERROR, get_command_name(commandcode));
		//return -1;
	//}
	
	//if(response->status_code == STATUS_SUCCESS)
		//log_info(PRU_SENDRECEIVE_STATUS_SUCCESS, get_command_name(commandcode));
	//else 
	//{ 
		//log_fnc_err(UNKNOWN_ERROR, PRU_SENDRECEIVE_STATUS_FAILURE, get_statuscode(response->status_code)); 
		//return -1;
	//}
	
	//log_info("Relevant Bits Per Sample: %d.\n", response->relevantbitspersamples);
	//log_info("Raw Samples Byte Count: %d.\n", response->bytecount);
	//log_info("Byte count: (%d), ", response->bytecount);
	//log_info("Bytes: ");
	//int i;
	//for(i=0;i<numbytespersample*numsamples;i++)
		//log_info("%2x ", response->rawbuffer[i]);
	//log_info("\n");
	
	//return 0;
//}
