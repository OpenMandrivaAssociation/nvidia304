# I love OpenSource :-(

## NOTE: When modifying this .spec, you do not necessarily need to care about
##       the %simple stuff. It is fine to break them, I'll fix it when I need them :)
## - Anssi

# %simple mode can be used to transform an arbitrary nvidia installer
# package to rpms, similar to %atibuild mode in fglrx.
# Macros version, rel, nsource, pkgname, distsuffix should be manually defined.
%define simple 0
%{?_without_simple: %global simple 0}
%{?_with_simple: %global simple 1}

%if !%simple
# When updating, please add new ids to ldetect-lst (merge2pcitable.pl)
%define version 304.125
%define rel 2
# the highest supported videodrv abi
%define videodrv_abi 19
%endif

%define priority 9630

# pkg0: plain archive
# pkg1: + precompiled modules
# pkg2: + 32bit compatibility libraries
%define pkgname32 NVIDIA-Linux-x86-%{version}
%define pkgname64 NVIDIA-Linux-x86_64-%{version}

# For now, backportability is kept for 2006.0 / CS4 forwards.

%define drivername nvidia304
%define driverpkgname x11-driver-video-%{drivername}
%define modulename %{drivername}
%define cards GeForce 6xxx and GeForce 7xxx cards
%define xorg_libdir %{_libdir}/xorg
%define xorg_extra_modules %{_libdir}/xorg/extra-modules
%define nvidia_driversdir %{_libdir}/%{drivername}/xorg
%define nvidia_extensionsdir %{_libdir}/%{drivername}/xorg
%define nvidia_modulesdir %{_libdir}/%{drivername}/xorg
%define nvidia_libdir %{_libdir}/%{drivername}
%define nvidia_libdir32 %{_prefix}/lib/%{drivername}
%define nvidia_bindir %{nvidia_libdir}/bin
%define nvidia_deskdir %{_datadir}/%{drivername}
%define nvidia_xvmcconfdir %{_sysconfdir}/%{drivername}
%define nvidia_xinitdir %{_sysconfdir}/%{drivername}
%define ld_so_conf_dir %{_sysconfdir}/%{drivername}
%define ld_so_conf_file ld.so.conf

# The entry in Cards+ this driver should be associated with, if there is
# no entry in ldetect-lst default pcitable:
# cooker ldetect-lst should be up-to-date
%define ldetect_cards_name %nil

%define biarches x86_64
%ifarch %{ix86}
%define nsource %{SOURCE0}
%define pkgname %{pkgname32}
%endif
%ifarch x86_64
%define nsource %{SOURCE1}
%define pkgname %{pkgname64}
%endif

# Other packages should not require any NVIDIA libraries, and this package
# should not be pulled in when libGL.so.1 is required
%define __noautoprov '^libGL\\.so\\.1(.*)|devel\\(libGL(.*)|\\.so'
%define common_requires_exceptions ^libGL\\.so\\|^libGLcore\\.so\\|^libnvidia.*\\.so

%ifarch %{biarches}
# (anssi) Allow installing of 64-bit package if the runtime dependencies
# of 32-bit libraries are not satisfied. If a 32-bit package that requires
# libGL.so.1 is installed, the 32-bit mesa libs are pulled in and that will
# pull the dependencies of 32-bit nvidia libraries in as well.
%define __noautoreq %common_requires_exceptions\\|^lib.*so\\.[^(]\\+\\(([^)]\\+)\\)\\?$
%else
%define __noautoreq %common_requires_exceptions
%endif

Summary:	NVIDIA proprietary X.org driver and libraries, 304.xx series
Name:		nvidia304
Version:	%{version}
Release:	%{rel}
Source0:	ftp://download.nvidia.com/XFree86/Linux-x86/%{version}/%{pkgname32}.run
Source1:	ftp://download.nvidia.com/XFree86/Linux-x86_64/%{version}/%{pkgname64}.run
# GPLv2 source code; see also http://cgit.freedesktop.org/~aplattner/
Source2:	ftp://download.nvidia.com/XFree86/nvidia-settings/nvidia-settings-%{version}.tar.bz2
Source3:	ftp://download.nvidia.com/XFree86/nvidia-xconfig/nvidia-xconfig-%{version}.tar.bz2
Source4:	nvidia-mdvbuild-skel
Source100:	nvidia304.rpmlintrc
# https://qa.mandriva.com/show_bug.cgi?id=39921
Patch1:		nvidia-settings-enable-dyntwinview-mdv.patch
# include xf86vmproto for X_XF86VidModeGetGammaRampSize, fixes build on cooker
Patch3:		nvidia-settings-include-xf86vmproto.patch
Patch4:		NVIDIA-Linux-x86_64-304.125-kernel-3.18.patch
PAtch5:		NVIDIA-Linux-x86_64-304.125-kernel-3.19.patch

License:	Freeware
URL:		http://www.nvidia.com/object/unix.html
Group:		System/Kernel and hardware
ExclusiveArch:	%{ix86} x86_64
BuildRequires:	imagemagick
BuildRequires:	pkgconfig(gtk+-x11-2.0)
BuildRequires:	pkgconfig(xxf86vm)
BuildRequires:	pkgconfig(gl)
BuildRequires:	pkgconfig(xv)
%if "%{driverpkgname}" == "nvidia"
# old nvidia package had different versioning
Epoch:		1
%endif

%description
Source package of the 304.88.xx series NVIDIA proprietary driver.
Binary packages are named x11-driver-video-nvidia304 on 2009 and later,
x11-driver-video-nvidia-current on 2008, nvidia97xx on 2007.1, and
nvidia on 2007.0 and earlier.

%package -n %{driverpkgname}
Summary:	NVIDIA proprietary X.org driver and libraries, 304.xx series
Group:		System/Kernel and hardware
# Older alternatives implementations were buggy in various ways:
Requires(post):	update-alternatives >= 1.9.0
Requires(postun):	update-alternatives >= 1.9.0
# Proprietary driver handling rework:
Conflicts:	harddrake < 10.4.163
Conflicts:	drakx-kbd-mouse-x11 < 0.21
Conflicts:	x11-server-common < 1.3.0.0-17
# Suggests supported as of 2008.0, pull the rest of docs:
Suggests:	%{drivername}-doc-html
# for missing libwfb.so
Conflicts:	x11-server-common < 1.4
# Proper support for versioned kmod() was added in 2008.1:
Requires:	kmod(%{modulename}) = %{version}
Conflicts:	x11-server-common < 1.6.0-11
Requires:	x11-server-common
# Conflict with the next videodrv ABI break.
# The NVIDIA driver supports the previous ABI versions as well and therefore
# a strict version-specific requirement would not be enough.
### This is problematic as it can cause removal of xserver instead (Anssi 04/2011)
###Conflicts:  xserver-abi(videodrv-%(echo $((%{videodrv_abi} + 1))))

%description -n %{driverpkgname}
NVIDIA proprietary X.org graphics driver, related libraries and
configuration tools for %cards,
including the associated Quadro cards.

NOTE: You should use XFdrake to configure your NVIDIA card. The
correct packages will be automatically installed and configured.

If you do not want to use XFdrake, see README.manual-setup.

This NVIDIA driver should be used with %cards,
including the associated Quadro cards.

%package -n dkms-%{drivername}
Summary:	NVIDIA kernel module for %cards
Group:		System/Kernel and hardware
Requires:	dkms
Requires(post):	dkms
Requires(preun):	dkms
Requires:	%{driverpkgname} = %{version}

%description -n dkms-%{drivername}
NVIDIA kernel module for %cards. This
is to be used with the %{driverpkgname} package.

%package -n %{drivername}-devel
Summary:	NVIDIA XvMC/OpenGL/CUDA development headers (%{drivername})
Group:		Development/C
Requires:	%{driverpkgname} = %{version}-%{release}
Requires:	%{drivername}-cuda-opencl = %{version}-%{release}

%description -n %{drivername}-devel
NVIDIA XvMC static development library and OpenGL headers for
%cards. This package is not required for
normal use.

%package -n %{drivername}-cuda-opencl
Summary:	CUDA and OpenCL libraries for NVIDIA proprietary driver (%{drivername})
Group:		System/Kernel and hardware
Requires:	%{driverpkgname} = %{version}-%{release}
Conflicts:	%{driverpkgname} < 304.14.25-2

%description -n %{drivername}-cuda-opencl
Cuda and OpenCL libraries for NVIDIA proprietary driver 
for %cards.
This package is not required for normal use, it provides libraries to
use NVIDIA cards for High Performance Computing (HPC).

# HTML doc splitted off because of size, for Mandriva One:
%package -n %{drivername}-doc-html
Summary:	NVIDIA html documentation (%{drivername})
Group:		System/Kernel and hardware
Requires:	%{driverpkgname} = %{version}-%{release}

%description -n %{drivername}-doc-html
HTML version of the README.txt file provided in package
%{driverpkgname}.

%prep
%setup -q -c -T -a 2 -a 3
cd nvidia-settings-%{version}
%patch1 -p1
%patch3 -p1
cd ..
sh %{nsource} --extract-only

%if !%simple
cd %{pkgname}
%patch4 -p1
%patch5 -p1
cd ..
%endif

rm -rf %{pkgname}/usr/src/nv/precompiled

%if %simple
# for old releases
mkdir -p %{pkgname}/kernel
%endif

# (tmb) nuke nVidia provided dkms.conf as we need our own
rm -rf %{pkgname}/kernel/dkms.conf

# install our own dkms.conf
cat > %{pkgname}/kernel/dkms.conf <<EOF
PACKAGE_NAME="%{drivername}"
PACKAGE_VERSION="%{version}-%{release}"
BUILT_MODULE_NAME[0]="nvidia"
DEST_MODULE_LOCATION[0]="/kernel/drivers/char/drm"
DEST_MODULE_NAME[0]="%{modulename}"
MAKE[0]="make SYSSRC=\${kernel_source_dir} module"
CLEAN="make -f Makefile.kbuild clean"
AUTOINSTALL="yes"
EOF

cat > README.install.urpmi <<EOF
This driver is for %cards.

Use XFdrake to configure X to use the correct NVIDIA driver. Any needed
packages will be automatically installed if not already present.
1. Run XFdrake as root.
2. Go to the Graphics Card list.
3. Select your card (it is usually already autoselected).
4. Answer any questions asked and then quit.

If you do not want to use XFdrake, see README.manual-setup.
EOF

cat > README.manual-setup <<EOF
This file describes the procedure for the manual installation of this NVIDIA
driver package. You can find the instructions for the recommended automatic
installation in the file 'README.install.urpmi' in this directory.

- Open %{_sysconfdir}/X11/xorg.conf and make the following changes:
o Change the Driver to "nvidia" in the Device section
o Make the line below the only 'glx' related line in the Module section,
adding it if it is not already there:
Load "glx"
o Remove any 'ModulePath' lines from the Files section
- Run "update-alternatives --set gl_conf %{_sysconfdir}/%{drivername}/ld.so.conf" as root.
- Run "ldconfig -X" as root.
EOF
mv %{pkgname}/html html-doc

# It wants to link Xxf86vm statically (presumably because it is somewhat more
# rare than the other dependencies)
sed -i 's|-Wl,-Bstatic||' nvidia-settings-%{version}/Makefile
sed -i 's|-O ||' nvidia-settings-%{version}/Makefile
sed -i 's|-O ||' nvidia-xconfig-%{version}/Makefile
rm nvidia-settings-%{version}/src/*/*.a

%build
%setup_compile_flags

%make -C nvidia-settings-%{version}/src/libXNVCtrl
%make -C nvidia-settings-%{version} STRIP_CMD=true
%make -C nvidia-xconfig-%{version} STRIP_CMD=true

%install
cd %{pkgname}

# dkms
install -d -m755 %{buildroot}%{_usrsrc}/%{drivername}-%{version}-%{release}

# menu entry
install -d -m755 %{buildroot}%{_datadir}/%{drivername}
cat > %{buildroot}%{_datadir}/%{drivername}/mandriva-nvidia-settings.desktop <<EOF
[Desktop Entry]
Name=NVIDIA Display Settings
Comment=Configure NVIDIA X driver
Exec=%{_bindir}/nvidia-settings
Icon=%{drivername}-settings
Terminal=false
Type=Application
Categories=GTK;Settings;HardwareSettings;X-MandrivaLinux-System-Configuration;
EOF

install -d -m755 %{buildroot}%{_datadir}/applications
touch %{buildroot}%{_datadir}/applications/mandriva-nvidia-settings.desktop

# icons
install -d -m755 %{buildroot}%{_iconsdir}/hicolor/{16x16,32x32,48x48}/apps
%if !%simple
convert nvidia-settings.png -resize 16x16 %{buildroot}%{_iconsdir}/hicolor/16x16/apps/%{drivername}-settings.png
convert nvidia-settings.png -resize 32x32 %{buildroot}%{_iconsdir}/hicolor/32x32/apps/%{drivername}-settings.png
convert nvidia-settings.png -resize 48x48 %{buildroot}%{_iconsdir}/hicolor/48x48/apps/%{drivername}-settings.png
%else
# no imagemagick
[ -e nvidia-settings.png ] || cp -a usr/share/pixmaps/nvidia-settings.png .
install -m644 nvidia-settings.png %{buildroot}%{_iconsdir}/hicolor/48x48/apps/%{drivername}-settings.png
%endif

error_fatal() {
    echo "Error: $@." >&2
    exit 1
}

error_unhandled() {
    echo "Warning: $@." >&2
    echo "Warning: $@." >> warns.log
%if !%simple
    # cause distro builds to fail in case of unhandled files
    exit 1
%endif
}

parseparams() {
    for value in $rest; do
	local param=$1
	[ -n "$param" ] || error_fatal "unhandled parameter $value"
	shift
	eval $param=$value

	[ -n "$value" ] || error_fatal "empty $param"

	# resolve libdir based on $arch
	if [ "$param" = "arch" ]; then
	    case "$arch" in
	    NATIVE)		nvidia_libdir=%{nvidia_libdir};;
	    COMPAT32)	nvidia_libdir=%{nvidia_libdir32};;
	    *)		error_fatal "unknown arch $arch"
	    esac
	fi
    done
}

add_to_list() {
%if !%simple
    # on distro builds, only use .manifest for %doc files
    [ "${2#%doc}" = "${2}" ] && return
%endif
    local list="$1.files"
    local entry="$2"
    echo $entry >> $list
}

install_symlink() {
    local pkg="$1"
    local dir="$2"
    mkdir -p %{buildroot}$dir
    ln -s $dest %{buildroot}$dir/$file
    add_to_list $pkg $dir/$file
}

install_lib_symlink() {
    local pkg="$1"
    local dir="$2"
    case "$file" in
    libvdpau_*.so)
	# vdpau drivers => not put into -devel
	;;
    *.so)
	pkg=nvidia-devel;;
    esac
    install_symlink $pkg $dir
}

install_file_only() {
    local pkg="$1"
    local dir="$2"
    mkdir -p %{buildroot}$dir
    # replace 0444 with more usual 0644
    [ "$perms" = "0444" ] && perms="0644"
    install -m $perms $file %{buildroot}$dir
}

install_file() {
    local pkg="$1"
    local dir="$2"
    install_file_only $pkg $dir
    add_to_list $pkg $dir/$(basename $file)
}

get_module_dir() {
    local subdir="$1"
    case "$subdir" in
    extensions*)	echo %{nvidia_extensionsdir};;
    drivers/)	echo %{nvidia_driversdir};;
    /)		echo %{nvidia_modulesdir};;
    *)		error_unhandled "unhandled module subdir $subdir"
	    echo %{nvidia_modulesdir};;
    esac
}

for file in nvidia.files nvidia-devel.files nvidia-cuda.files nvidia-dkms.files nvidia-html.files; do
    rm -f $file
    touch $file
done

# install files according to .manifest
cat .manifest | tail -n +9 | while read line; do
    rest=${line}
    file=${rest%%%% *}
    rest=${rest#* }
    perms=${rest%%%% *}
    rest=${rest#* }
    type=${rest%%%% *}
    rest=${rest#* }

    case "$type" in
    CUDA_LIB)
	    parseparams arch subdir
	    install_file nvidia-cuda $nvidia_libdir/$subdir
	    ;;
    CUDA_SYMLINK)
	    parseparams arch subdir dest
	    install_lib_symlink nvidia-cuda $nvidia_libdir/$subdir
	    ;;
    NVCUVID_LIB)
	    parseparams arch
	    install_file nvidia-cuda $nvidia_libdir
	    ;;
    NVCUVID_LIB_SYMLINK)
	    parseparams arch dest
	    install_lib_symlink nvidia-cuda $nvidia_libdir
	    ;;
    OPENGL_LIB)
	    parseparams arch
	    install_file nvidia $nvidia_libdir
	    ;;
    OPENGL_SYMLINK)
	    parseparams arch dest
	    install_lib_symlink nvidia $nvidia_libdir
	    ;;
    TLS_LIB)
	    parseparams arch style subdir
	    install_file nvidia $nvidia_libdir/$subdir
	    ;;
    TLS_SYMLINK)
	    parseparams arch style subdir dest
	    install_lib_symlink nvidia $nvidia_libdir/$subdir
	    ;;
    UTILITY_LIB)
	    install_file nvidia %{nvidia_libdir}
	    ;;
    UTILITY_LIB_SYMLINK)
	    parseparams dest
	    install_lib_symlink nvidia %{nvidia_libdir}
	    ;;
    VDPAU_LIB)
	    parseparams arch subdir
	    # on 2009.0+, only install libvdpau_nvidia.so
	    case $file in *libvdpau_nvidia.so*);; *) continue; esac
	    install_file nvidia $nvidia_libdir/$subdir
	    ;;
    VDPAU_SYMLINK)
	    parseparams arch subdir dest
	    # on 2009.0+, only install libvdpau_nvidia.so
	    case $file in *libvdpau_nvidia.so*);; *) continue; esac
	    install_lib_symlink nvidia $nvidia_libdir/$subdir
	    ;;
    XLIB_STATIC_LIB)
	    install_file nvidia-devel %{nvidia_libdir}
	    ;;
    XLIB_SHARED_LIB)
	    install_file nvidia %{nvidia_libdir}
	    ;;
    XLIB_SYMLINK)
	    parseparams dest
	    install_lib_symlink nvidia %{nvidia_libdir}
	    ;;
    LIBGL_LA)
	    # (Anssi) we don't install .la files
	    ;;
    XMODULE_SHARED_LIB|GLX_MODULE_SHARED_LIB)
	    parseparams subdir
	    install_file nvidia $(get_module_dir $subdir)
	    ;;
    XMODULE_NEWSYM)
	    # symlink that is created only if it doesn't already
	    # exist (i.e. as part of x11-server)
	    case "$file" in
	    libwfb.so)
	    # 2008.1+ has this one already
		    continue
		    ;;
	    *)
		    error_unhandled "unknown XMODULE_NEWSYM type file $file, skipped"
		    continue
	    esac
	    parseparams subdir dest
	    install_symlink nvidia $(get_module_dir $subdir)
	    ;;
	XORG_OUTPUTCLASS_CONFIG)
		# dont install xorg driver autoloader conf
		continue
		;;
    XMODULE_SYMLINK|GLX_MODULE_SYMLINK)
	    parseparams subdir dest
	    install_symlink nvidia $(get_module_dir $subdir)
	    ;;
    VDPAU_HEADER)
	    # already in vdpau-devel
	    continue
	    parseparams subdir
	    install_file_only nvidia-devel %{_includedir}/%{drivername}/$subdir
	    ;;
    OPENGL_HEADER|CUDA_HEADER)
	    parseparams subdir
	    install_file_only nvidia-devel %{_includedir}/%{drivername}/$subdir
	    ;;
    DOCUMENTATION)
	    parseparams subdir
	    case $subdir in
	    */html)
			add_to_list nvidia-html "%%doc %{pkgname}/$file"
			continue
			;;
	    */include/*)
			continue
			;;
	    esac
	    case $file in
	    *XF86Config*|*nvidia-settings.png)
			continue;;
	    esac
	    add_to_list nvidia "%%doc %{pkgname}/$file"
	    ;;
    MANPAGE)
	    parseparams subdir
	    case "$file" in
	    *nvidia-installer*)
			# not installed
			continue
			;;
	    *nvidia-settings*|*nvidia-xconfig*|*nvidia-cuda*)
%if !%simple
			# installed separately below
			continue
%endif
			;;
	    *nvidia-smi*)
			# ok
			;;
	    *)
			error_unhandled "skipped unknown man page $(basename $file)"
			continue
	    esac
	    install_file_only nvidia %{_mandir}/$subdir
	    ;;
    UTILITY_BINARY)
	    case "$file" in
	    *nvidia-settings|*nvidia-xconfig|*nvidia-cuda*)
%if !%simple
			# not installed, we install our own copy
			continue
%endif
			;;
	    *nvidia-smi|*nvidia-bug-report.sh|*nvidia-debugdump)
			# ok
			;;
	    *)
			error_unhandled "unknown binary $(basename $file) will be installed to %{nvidia_bindir}/$(basename $file)"
			;;
	    esac
	    install_file nvidia %{nvidia_bindir}
	    ;;
    UTILITY_BIN_SYMLINK)
	    case $file in nvidia-uninstall) continue;; esac
	    parseparams dest
	    install_symlink nvidia %{nvidia_bindir}
	    ;;
    INSTALLER_BINARY)
	    # not installed
	    ;;
    KERNEL_MODULE_SRC)
	    install_file nvidia-dkms %{_usrsrc}/%{drivername}-%{version}-%{release}
	    ;;
    CUDA_ICD)
	    # in theory this should go to the cuda subpackage, but it goes into the main package
	    # as this avoids one broken symlink and it is small enough to not cause space issues
	    install_file nvidia %{_sysconfdir}/%{drivername}
	    ;;
    DOT_DESKTOP)
	    # we provide our own for now
	    ;;
    *)
	    error_unhandled "file $(basename $file) of unknown type $type will be skipped"
    esac
done

[ -z "$warnings" ] || echo "Please inform Anssi Hannula <anssi@mandriva.org> or http://qa.mandriva.com/ of the above warnings." >> warns.log

%if %simple
find %{buildroot}%{_libdir} %{buildroot}%{_prefix}/lib -type d | while read dir; do
dir=${dir#%{buildroot}}
echo "$dir" | grep -q nvidia && echo "%%dir $dir" >> nvidia.files
done
[ -d %{buildroot}%{_includedir}/%{drivername} ] && echo "%{_includedir}/%{drivername}" >> nvidia-devel.files

# for old releases in %%simple mode
if ! [ -e %{buildroot}%{_usrsrc}/%{drivername}-%{version}-%{release}/dkms.conf ]; then
	install -m644 kernel/dkms.conf %{buildroot}%{_usrsrc}/%{drivername}-%{version}-%{release}/dkms.conf
fi
%endif

%if !%simple
# confirm SONAME; if something else than libvdpau_nvidia.so or libvdpau_nvidia.so.1, adapt .spec as needed:
[ "$(objdump -p %{buildroot}%{nvidia_libdir}/vdpau/libvdpau_nvidia.so.%{version} | grep SONAME | gawk '{ print $2 }')" = "libvdpau_nvidia.so.1" ]

rm -f %{buildroot}%{nvidia_libdir}/vdpau/libvdpau_nvidia.so.1
rm -f %{buildroot}%{nvidia_libdir32}/vdpau/libvdpau_nvidia.so.1
%endif

# vdpau alternative symlink
install -d -m755 %{buildroot}%{_libdir}/vdpau
touch %{buildroot}%{_libdir}/vdpau/libvdpau_nvidia.so.1
%ifarch %{biarches}
install -d -m755 %{buildroot}%{_prefix}/lib/vdpau
touch %{buildroot}%{_prefix}/lib/vdpau/libvdpau_nvidia.so.1
%endif

%if !%simple
# self-built binaries
install -m755 ../nvidia-settings-%{version}/src/_out/*/nvidia-settings %{buildroot}%{nvidia_bindir}
install -m755 ../nvidia-xconfig-%{version}/_out/*/nvidia-xconfig %{buildroot}%{nvidia_bindir}
%endif
# binary alternatives
install -d -m755 %{buildroot}%{_bindir}
touch %{buildroot}%{_bindir}/nvidia-settings
touch %{buildroot}%{_bindir}/nvidia-smi
touch %{buildroot}%{_bindir}/nvidia-debugdump
touch %{buildroot}%{_bindir}/nvidia-xconfig
touch %{buildroot}%{_bindir}/nvidia-bug-report.sh
# rpmlint:
chmod 0755 %{buildroot}%{_bindir}/*

%if !%simple
# install man pages
install -m755 ../nvidia-settings-%{version}/doc/_out/*/nvidia-settings.1 %{buildroot}%{_mandir}/man1
install -m755 ../nvidia-xconfig-%{version}/_out/*/nvidia-xconfig.1 %{buildroot}%{_mandir}/man1
%endif
# bug #41638 - whatis entries of nvidia man pages appear wrong
gunzip %{buildroot}%{_mandir}/man1/*.gz
sed -r -i '/^nvidia\\-[a-z]+ \\- NVIDIA/s,^nvidia\\-,nvidia-,' %{buildroot}%{_mandir}/man1/*.1
cd %{buildroot}%{_mandir}/man1
rename nvidia alt-%{drivername} *
cd -
touch %{buildroot}%{_mandir}/man1/nvidia-xconfig.1%{_extension}
touch %{buildroot}%{_mandir}/man1/nvidia-settings.1%{_extension}
touch %{buildroot}%{_mandir}/man1/nvidia-smi.1%{_extension}

# cuda nvidia.icd
install -d -m755 %{buildroot}%{_sysconfdir}/OpenCL/vendors
touch %{buildroot}%{_sysconfdir}/OpenCL/vendors/nvidia.icd
# override apparently wrong reference to the development symlink name:
[ "$(cat %{buildroot}%{_sysconfdir}/%{drivername}/nvidia.icd)" = "libcuda.so" ] &&
echo libcuda.so.1 > %{buildroot}%{_sysconfdir}/%{drivername}/nvidia.icd

# ld.so.conf
install -d -m755 %{buildroot}%{_sysconfdir}/%{drivername}
echo "%{nvidia_libdir}" > %{buildroot}%{_sysconfdir}/%{drivername}/ld.so.conf
%ifarch %{biarches}
echo "%{nvidia_libdir32}" >> %{buildroot}%{_sysconfdir}/%{drivername}/ld.so.conf
%endif
install -d -m755 %{buildroot}%{_sysconfdir}/ld.so.conf.d
touch %{buildroot}%{_sysconfdir}/ld.so.conf.d/GL.conf

# modprobe.conf
install -d -m755 %{buildroot}%{_sysconfdir}/modprobe.d
touch %{buildroot}%{_sysconfdir}/modprobe.d/display-driver.conf
echo "install nvidia /sbin/modprobe %{modulename} \$CMDLINE_OPTS" > %{buildroot}%{_sysconfdir}/%{drivername}/modprobe.conf

# XvMCConfig
install -d -m755 %{buildroot}%{_sysconfdir}/%{drivername}
echo "libXvMCNVIDIA_dynamic.so.1" > %{buildroot}%{_sysconfdir}/%{drivername}/XvMCConfig

# xinit script
install -d -m755 %{buildroot}%{_sysconfdir}/%{drivername}
cat > %{buildroot}%{_sysconfdir}/%{drivername}/nvidia-settings.xinit <<EOF
# to be sourced
#
# Do not modify this file; the changes will be overwritten.
# If you want to disable automatic configuration loading, create
# /etc/sysconfig/nvidia-settings with this line: LOAD_NVIDIA_SETTINGS="no"
#
LOAD_NVIDIA_SETTINGS="yes"
[ -f %{_sysconfdir}/sysconfig/nvidia-settings ] && . %{_sysconfdir}/sysconfig/nvidia-settings
[ "\$LOAD_NVIDIA_SETTINGS" = "yes" ] && %{_bindir}/nvidia-settings --load-config-only
EOF
chmod 0755 %{buildroot}%{_sysconfdir}/%{drivername}/nvidia-settings.xinit
install -d -m755 %{buildroot}%{_sysconfdir}/X11/xinit.d
touch %{buildroot}%{_sysconfdir}/X11/xinit.d/nvidia-settings.xinit

# install ldetect-lst pcitable files for backports
# local version of merge2pcitable.pl:read_nvidia_readme:
section=0
set +x
[ -e README.txt ] || cp -a usr/share/doc/README.txt .
cat README.txt | while read line; do
[ $section -gt 3 ] && break
if [ $((section %% 2)) -eq 0 ]; then
echo "$line" | grep -Pq "^\s*NVIDIA GPU product\s+Device PCI ID.*" && section=$((section+1))
continue
fi
if echo "$line" | grep -Pq "^\s*$"; then
section=$((section+1))
continue
fi
echo "$line" | grep -Pq "^\s*-+[\s-]+$" && continue
id=$(echo "$line" | sed -nre 's,^\s*.+?\s+0x(....).*$,\1,p' | tr '[:upper:]' '[:lower:]')
echo "0x10de 0x$id \"Card:%{ldetect_cards_name}\""
done | sort -u > pcitable.nvidia.lst
set -x
[ $(wc -l pcitable.nvidia.lst | cut -f1 -d" ") -gt 200 ]
%if "%{ldetect_cards_name}" != ""
install -d -m755 %{buildroot}%{_datadir}/ldetect-lst/pcitable.d
gzip -c pcitable.nvidia.lst > %{buildroot}%{_datadir}/ldetect-lst/pcitable.d/40%{drivername}.lst.gz
%endif

export EXCLUDE_FROM_STRIP="$(find %{buildroot} -type f \! -name nvidia-settings \! -name nvidia-xconfig)"


%post -n %{driverpkgname}
# XFdrake used to generate an nvidia.conf file
[ -L %{_sysconfdir}/modprobe.d/nvidia.conf ] || rm -f %{_sysconfdir}/modprobe.d/nvidia.conf

current_glconf="$(readlink -e %{_sysconfdir}/ld.so.conf.d/GL.conf)"

# owned by libvdpau1, created in case libvdpau1 is installed only just after
# this package
mkdir -p %{_libdir}/vdpau

%{_sbindir}/update-alternatives \
    --install %{_sysconfdir}/ld.so.conf.d/GL.conf gl_conf %{_sysconfdir}/%{drivername}/ld.so.conf %{priority} \
    --slave %{_mandir}/man1/nvidia-settings.1%{_extension} man_nvidiasettings%{_extension} %{_mandir}/man1/alt-%{drivername}-settings.1%{_extension} \
    --slave %{_mandir}/man1/nvidia-xconfig.1%{_extension} man_nvidiaxconfig%{_extension} %{_mandir}/man1/alt-%{drivername}-xconfig.1%{_extension} \
    --slave %{_mandir}/man1/nvidia-smi.1%{_extension} nvidia-smi.1%{_extension} %{_mandir}/man1/alt-%{drivername}-smi.1%{_extension} \
    --slave %{_datadir}/applications/mageia-nvidia-settings.desktop nvidia_desktop %{_datadir}/%{drivername}/mageia-nvidia-settings.desktop \
    --slave %{_bindir}/nvidia-settings nvidia_settings %{nvidia_bindir}/nvidia-settings \
    --slave %{_bindir}/nvidia-smi nvidia_smi %{nvidia_bindir}/nvidia-smi \
    --slave %{_bindir}/nvidia-xconfig nvidia_xconfig %{nvidia_bindir}/nvidia-xconfig \
    --slave %{_bindir}/nvidia-debugdump nvidia-debugdump %{nvidia_bindir}/nvidia-debugdump \
    --slave %{_bindir}/nvidia-bug-report.sh nvidia_bug_report %{nvidia_bindir}/nvidia-bug-report.sh \
    --slave %{_sysconfdir}/X11/XvMCConfig xvmcconfig %{_sysconfdir}/%{drivername}/XvMCConfig \
    --slave %{_sysconfdir}/X11/xinit.d/nvidia-settings.xinit nvidia-settings.xinit %{_sysconfdir}/%{drivername}/nvidia-settings.xinit \
    --slave %{_libdir}/vdpau/libvdpau_nvidia.so.1 %{_lib}vdpau_nvidia.so.1 %{nvidia_libdir}/vdpau/libvdpau_nvidia.so.%{version} \
    --slave %{_sysconfdir}/modprobe.d/display-driver.conf display-driver.conf %{_sysconfdir}/%{drivername}/modprobe.conf \
    --slave %{_sysconfdir}/OpenCL/vendors/nvidia.icd nvidia.icd %{_sysconfdir}/%{drivername}/nvidia.icd \
%ifarch %{biarches}
    --slave %{_prefix}/lib/vdpau/libvdpau_nvidia.so.1 libvdpau_nvidia.so.1 %{nvidia_libdir32}/vdpau/libvdpau_nvidia.so.%{version} \
%endif
    --slave %{xorg_extra_modules} xorg_extra_modules %{nvidia_extensionsdir} \

if [ "${current_glconf}" = "%{_sysconfdir}/nvidia97xx/ld.so.conf" ]; then
    # Adapt for the renaming of the driver. X.org config still has the old ModulePaths
    # but they do not matter as we are using alternatives for libglx.so now.
    %{_sbindir}/update-alternatives --set gl_conf %{_sysconfdir}/%{drivername}/ld.so.conf
fi
# explicit /sbin/ldconfig due to alternatives
/sbin/ldconfig -X

%if "%{ldetect_cards_name}" != ""
[ -x %{_sbindir}/update-ldetect-lst ] && %{_sbindir}/update-ldetect-lst || :
%endif

%postun -n %{driverpkgname}
if [ ! -f %{_sysconfdir}/%{drivername}/ld.so.conf ]; then
  %{_sbindir}/update-alternatives --remove gl_conf %{_sysconfdir}/%{drivername}/ld.so.conf
fi
# explicit /sbin/ldconfig due to alternatives
/sbin/ldconfig -X

%if "%{ldetect_cards_name}" != ""
[ -x %{_sbindir}/update-ldetect-lst ] && %{_sbindir}/update-ldetect-lst || :
%endif

%post -n %{drivername}-cuda-opencl
# explicit /sbin/ldconfig due to a non-standard library directory
/sbin/ldconfig -X

%post -n dkms-%{drivername}
/usr/sbin/dkms --rpm_safe_upgrade add -m %{drivername} -v %{version}-%{release} &&
/usr/sbin/dkms --rpm_safe_upgrade build -m %{drivername} -v %{version}-%{release} &&
/usr/sbin/dkms --rpm_safe_upgrade install -m %{drivername} -v %{version}-%{release} --force

# rmmod any old driver if present and not in use (e.g. by X)
rmmod nvidia > /dev/null 2>&1 || true

%preun -n dkms-%{drivername}
/usr/sbin/dkms --rpm_safe_upgrade remove -m %{drivername} -v %{version}-%{release} --all

# rmmod any old driver if present and not in use (e.g. by X)
rmmod nvidia > /dev/null 2>&1 || true

%files -n %{driverpkgname}
%doc README.install.urpmi README.manual-setup

%if "%{ldetect_cards_name}" != ""
%{_datadir}/ldetect-lst/pcitable.d/40%{drivername}.lst.gz
%endif

# ld.so.conf, modprobe.conf, xvmcconfig, xinit
%ghost %{_sysconfdir}/ld.so.conf.d/GL.conf
%ghost %{_sysconfdir}/X11/xinit.d/nvidia-settings.xinit
%ghost %{_sysconfdir}/modprobe.d/display-driver.conf
%dir %{_sysconfdir}/%{drivername}
%{_sysconfdir}/%{drivername}/modprobe.conf
%{_sysconfdir}/%{drivername}/ld.so.conf
%{_sysconfdir}/%{drivername}/XvMCConfig
%{_sysconfdir}/%{drivername}/nvidia-settings.xinit
%if !%simple
%{_sysconfdir}/%{drivername}/nvidia.icd
%endif

%dir %{_sysconfdir}/OpenCL
%dir %{_sysconfdir}/OpenCL/vendors
%ghost %{_sysconfdir}/OpenCL/vendors/nvidia.icd

%ghost %{_bindir}/nvidia-settings
%ghost %{_bindir}/nvidia-smi
%ghost %{_bindir}/nvidia-debugdump
%ghost %{_bindir}/nvidia-xconfig
%ghost %{_bindir}/nvidia-bug-report.sh
%dir %{nvidia_bindir}
%{nvidia_bindir}/nvidia-settings
%{nvidia_bindir}/nvidia-smi
%{nvidia_bindir}/nvidia-debugdump
%{nvidia_bindir}/nvidia-xconfig
%{nvidia_bindir}/nvidia-bug-report.sh

%ghost %{_mandir}/man1/nvidia-xconfig.1%{_extension}
%ghost %{_mandir}/man1/nvidia-settings.1%{_extension}
%ghost %{_mandir}/man1/nvidia-smi.1%{_extension}
%{_mandir}/man1/alt-%{drivername}-xconfig.1*
%{_mandir}/man1/alt-%{drivername}-settings.1*
%{_mandir}/man1/alt-%{drivername}-smi.1*

%ghost %{_datadir}/applications/mandriva-nvidia-settings.desktop
%dir %{nvidia_deskdir}
%{nvidia_deskdir}/mandriva-nvidia-settings.desktop

%if !%simple
%{_iconsdir}/hicolor/16x16/apps/%{drivername}-settings.png
%{_iconsdir}/hicolor/32x32/apps/%{drivername}-settings.png
%endif
%{_iconsdir}/hicolor/48x48/apps/%{drivername}-settings.png

%dir %{nvidia_libdir}
%dir %{nvidia_libdir}/tls
%dir %{nvidia_libdir}/vdpau
%{nvidia_libdir}/libGL.so.1
%{nvidia_libdir}/libGL.so.%{version}
%{nvidia_libdir}/libnvidia-glcore.so.%{version}
%{nvidia_libdir}/libXvMCNVIDIA_dynamic.so.1
%{nvidia_libdir}/libXvMCNVIDIA.so.%{version}
%{nvidia_libdir}/libnvidia-cfg.so.1
%{nvidia_libdir}/libnvidia-cfg.so.%{version}
%{nvidia_libdir}/libnvidia-tls.so.%{version}
%{nvidia_libdir}/libnvidia-ml.so.1
%{nvidia_libdir}/libnvidia-ml.so.%{version}
%{nvidia_libdir}/tls/libnvidia-tls.so.%{version}
%{nvidia_libdir}/vdpau/libvdpau_nvidia.so.%{version}
%ifarch %{biarches}
%dir %{nvidia_libdir32}
%dir %{nvidia_libdir32}/tls
%dir %{nvidia_libdir32}/vdpau
%{nvidia_libdir32}/libGL.so.1
%{nvidia_libdir32}/libGL.so.%{version}
%{nvidia_libdir32}/libnvidia-glcore.so.%{version}
%{nvidia_libdir32}/libnvidia-tls.so.%{version}
%{nvidia_libdir32}/tls/libnvidia-tls.so.%{version}
%{nvidia_libdir32}/libnvidia-ml.so.1
%{nvidia_libdir32}/libnvidia-ml.so.%{version}
%{nvidia_libdir32}/vdpau/libvdpau_nvidia.so.%{version}
%endif

%ghost %{_libdir}/vdpau/libvdpau_nvidia.so.1
%ifarch %{biarches}
# avoid unowned directory
%dir %{_prefix}/lib/vdpau
%ghost %{_prefix}/lib/vdpau/libvdpau_nvidia.so.1
%endif

%dir %{nvidia_modulesdir}
%{nvidia_modulesdir}/libnvidia-wfb.so.1

%{nvidia_modulesdir}/libnvidia-wfb.so.%{version}

%{nvidia_extensionsdir}/libglx.so.%{version}
%{nvidia_extensionsdir}/libglx.so

%{nvidia_driversdir}/nvidia_drv.so

%files -n %{drivername}-devel
%{_includedir}/%{drivername}
%{nvidia_libdir}/libXvMCNVIDIA.a
%{nvidia_libdir}/libXvMCNVIDIA_dynamic.so
%{nvidia_libdir}/libGL.so
%{nvidia_libdir}/libcuda.so
%{nvidia_libdir}/libnvcuvid.so
%{nvidia_libdir}/libnvidia-cfg.so
%{nvidia_libdir}/libnvidia-ml.so
%{nvidia_libdir}/libOpenCL.so
%{nvidia_libdir}/libvdpau_nvidia.so

%ifarch %{biarches}
%{nvidia_libdir32}/libGL.so
%{nvidia_libdir32}/libcuda.so
%{nvidia_libdir32}/libnvidia-ml.so
%{nvidia_libdir32}/libOpenCL.so
%{nvidia_libdir32}/libvdpau_nvidia.so
%endif

%files -n dkms-%{drivername}
%doc %{pkgname}/LICENSE
%{_usrsrc}/%{drivername}-%{version}-%{release}

%files -n %{drivername}-doc-html
%doc html-doc/*

%files -n %{drivername}-cuda-opencl -f %pkgname/nvidia-cuda.files
%if !%simple
%{nvidia_libdir}/libOpenCL.so.1.0.0
%{nvidia_libdir}/libOpenCL.so.1.0
%{nvidia_libdir}/libOpenCL.so.1
%{nvidia_libdir}/libnvidia-compiler.so.%{version}
%{nvidia_libdir}/libcuda.so.%{version}
%{nvidia_libdir}/libcuda.so.1
%{nvidia_libdir}/libnvidia-opencl.so.%{version}
%{nvidia_libdir}/libnvidia-opencl.so.1
%{nvidia_libdir}/libnvcuvid.so.%{version}
%{nvidia_libdir}/libnvcuvid.so.1
%ifarch %{biarches}
%{nvidia_libdir32}/libOpenCL.so.1.0.0
%{nvidia_libdir32}/libOpenCL.so.1.0
%{nvidia_libdir32}/libOpenCL.so.1
%{nvidia_libdir32}/libnvidia-compiler.so.%{version}
%{nvidia_libdir32}/libnvidia-opencl.so.%{version}
%{nvidia_libdir32}/libnvidia-opencl.so.1
%{nvidia_libdir32}/libcuda.so.%{version}
%{nvidia_libdir32}/libcuda.so.1
%endif
%endif
