Microsoft OCS Rack Manager BSP
===========================

Building the BSP
-------------------

###Getting the BSP code

To get the BSP you need to have `repo` installed and use it as:

Install the `repo` utility:

```bash
mkdir ~/bin
curl http://commondatastorage.googleapis.com/git-repo-downloads/repo > ~/bin/repo
chmod a+x ~/bin/repo
```

Download the BSP source:

```bash
PATH=${PATH}:~/bin
mkdir rackmanager-bsp
cd rackmanager-bsp
repo init -u https://github.com/Project-Olympus/rackmanager-bsp.git -b master
repo sync
```

### Building Images

Once this is completed, everything needing for a build is available.

To build a complete image:
```bash
./buildImage
```

After the build is done, the image files are available under `yoctoBuilds/images`

To build just the main QPSI image:
```bash
source yocto/oe-init-build-env yoctoBuilds
bitbake -R conf/local.conf core-image-msocs
```

To build just the upgrade eMMC image:
```bash
source yocto/oe-init-build-env yoctoBuilds
bitbake -R conf/initramfs.conf core-flasher-msocs
```

Development and Pushing Local Changes
-------------------------------------------------

If this copy of the source code is being used to make changes that need to be pushed back to the
remote repository, the local git repositories need to be configured to track the remote branch.
This is because `repo` will create the local repositories in a detached HEAD state. Do this before
making any changes to the local code.

To track the remote branch one of the following should be executed:

```bash
repo start master rackmanager meta-rackmanager rackmanager-build
```

Or in each of the local repositories that will be modified:

```bash
git checkout --track ocs/master
```

Once this is done, changes can be pushed back to the remote repository with

```bash
git push ocs master
```

