%define buildid 101.185

# We have to override the new %%install behavior because, well... the kernel is special.
%global __spec_install_pre %%{___build_pre}

Summary: The Linux kernel

# Sign modules on x86.  Make sure the config files match this setting if more
# architectures are added.
%ifarch %{ix86} x86_64
%global signmodules 1
%else
%global signmodules 0
%endif

# Amazon: no signing yet
%if %{?amzn}
%global signmodules 0
%endif

# Save original buildid for later if it's defined
%if 0%{?buildid:1}
%global orig_buildid %{buildid}
%undefine buildid
%endif

###################################################################
# Polite request for people who spin their own kernel rpms:
# please modify the "buildid" define in a way that identifies
# that the kernel isn't the stock distribution kernel, for example,
# by setting the define to ".local" or ".bz123456". This will be
# appended to the full kernel version.
#
# (Uncomment the '#' and both spaces below to set the buildid.)
#
# %% define buildid .local
###################################################################

# The buildid can also be specified on the rpmbuild command line
# by adding --define="buildid .whatever". If both the specfile and
# the environment define a buildid they will be concatenated together.
%if 0%{?orig_buildid:1}
%if 0%{?buildid:1}
%global srpm_buildid %{buildid}
%define buildid %{srpm_buildid}%{orig_buildid}
%else
%define buildid %{orig_buildid}
%endif
%endif

# what kernel is it we are building
%global kversion 4.14.158
%define rpmversion %{kversion}

# What parts do we want to build?  We must build at least one kernel.
# These are the kernels that are built IF the architecture allows it.
# All should default to 1 (enabled) and be flipped to 0 (disabled)
# by later arch-specific checks.

# The following build options are enabled by default.
# Use either --without <opt> in your rpmbuild command or force values
# to 0 in here to disable them.
#
# standard kernel
%define with_up        %{?_without_up:        0} %{?!_without_up:        1}
# kernel-debug
%define with_debug     %{?_without_debug:     0} %{?!_without_debug:     0}
# kernel-doc
%define with_doc       %{?_without_doc:       0} %{?!_without_doc:       0}
# kernel-headers
%define with_headers   %{?_without_headers:   0} %{?!_without_headers:   1}
# perf
%define with_perf      %{?_without_perf:      0} %{?!_without_perf:      1}
# tools
%define with_tools     %{?_without_tools:     0} %{?!_without_tools:     1}
# kernel-debuginfo
%define with_debuginfo %{?_without_debuginfo: 0} %{?!_without_debuginfo: 1}
# Want to build a the vsdo directories installed
%define with_vdso_install %{?_without_vdso_install: 0} %{?!_without_vdso_install: 1}
# Use dracut instead of mkinitrd for initrd image generation
%define with_dracut       %{?_without_dracut:       0} %{?!_without_dracut:       1}

# Build the kernel-doc package, but don't fail the build if it botches.
# Here "true" means "continue" and "false" means "fail the build".
%define doc_build_fail true

# should we do C=1 builds with sparse
%define with_sparse	%{?_with_sparse:      1} %{?!_with_sparse:      0}

# Set debugbuildsenabled to 1 for production (build separate debug kernels)
#  and 0 for rawhide (all kernels are debug kernels).
# See also 'make debug' and 'make release'.
%define debugbuildsenabled 0

# do we want the oldconfig run over the config files (when regenerating
# configs this should be avoided in order to save duplicate work...)
%define with_oldconfig     %{?_without_oldconfig:      0} %{?!_without_oldconfig:      1}

# pkg_release is what we'll fill in for the rpm Release: field
%define pkg_release %{?buildid}%{?dist}

%define make_target bzImage

%define KVERREL %{version}-%{release}.%{_target_cpu}
%define hdrarch %_target_cpu
%define asmarch %_target_cpu

%if !%{debugbuildsenabled}
%define with_debug 0
%endif

%if !%{with_debuginfo}
%define _enable_debug_packages 0
%endif
%define debuginfodir /usr/lib/debug

%define all_x86 i386 i686

%if %{with_vdso_install}
# These arches install vdso/ directories.
%define vdso_arches %{all_x86} x86_64 %{arm}
%endif

# Overrides for generic default options

# don't do debug builds on anything but i686 and x86_64
%ifnarch i686 x86_64 %{arm}
%define with_debug 0
%endif

# only package docs noarch
%ifnarch noarch
%define with_doc 0
%endif

# don't build noarch kernels or headers (duh)
%ifarch noarch
%define with_up 0
%define with_headers 0
%define with_tools 0
%define with_perf 0
%define all_arch_configs kernel-%{version}-*.config
%endif

# Per-arch tweaks

%ifarch %{all_x86}
%define asmarch x86
%define hdrarch i386
%define all_arch_configs kernel-%{version}-i?86*.config
%define image_install_path boot
%define kernel_image arch/%{asmarch}/boot/bzImage
%endif

%ifarch x86_64
%define asmarch x86
%define all_arch_configs kernel-%{version}-x86_64*.config
%define image_install_path boot
%define kernel_image arch/%{asmarch}/boot/bzImage
%endif

%ifarch %{arm}
%define all_arch_configs kernel-%{version}-arm*.config
%define asmarch arm
%define hdrarch arm
%define image_install_path boot
%define kernel_image arch/%{asmarch}/boot/zImage
%endif

# amazon: don't use nonint config target - we want to know when our config files are
# not complete
%define oldconfig_target oldconfig

# To temporarily exclude an architecture from being built, add it to
# %%nobuildarches. Do _NOT_ use the ExclusiveArch: line, because if we
# don't build kernel-headers then the new build system will no longer let
# us use the previous build of that package -- it'll just be completely AWOL.
# Which is a BadThing(tm).

# We don't build a kernel on i386; we only do kernel-headers there
%define nobuildarches i386 i486 i586

%ifarch %nobuildarches
%define with_up 0
%define with_debuginfo 0
%define with_perf 0
%define with_tools 0
%define _enable_debug_packages 0
%endif

# Architectures we build tools/cpupower on
%define cpupowerarchs %{ix86} x86_64
#define cpupowerarchs none

#
# Three sets of minimum package version requirements in the form of Conflicts:
# to versions below the minimum
#

#
# First the general kernel 2.6 required versions as per
# Documentation/Changes
#
%define kernel_dot_org_conflicts  ppp < 2.4.3-3, isdn4k-utils < 3.2-32, nfs-utils < 1.2.5-7.fc17, e2fsprogs < 1.37-4, util-linux < 2.12, jfsutils < 1.1.7-2, reiserfs-utils < 3.6.19-2, xfsprogs < 2.6.13-4, procps < 3.2.5-6.3, oprofile < 0.9.1-2, device-mapper-libs < 1.02.63-2, mdadm < 3.2.1-5

#
# Then a series of requirements that are distribution specific, either
# because we add patches for something, or the older versions have
# problems with the newer kernel or lack certain things that make
# integration in the distro harder than needed.
#
%define package_conflicts initscripts < 7.23, udev < 063-6, iptables < 1.3.2-1, selinux-policy-targeted < 1.25.3-14, squashfs-tools < 4.0, nvidia-dkms < 2:352.99-2017.03.104.amzn1, amdgpu-pro-dkms < 16.60-378247.2.amzn1

# We moved the drm include files into kernel-headers, make sure there's
# a recent enough libdrm-devel on the system that doesn't have those.
%define kernel_headers_conflicts libdrm-devel < 2.4.0-0.15

#
# Packages that need to be installed before the kernel is, because the %%post
# scripts use them.
#
%define kernel_prereq  fileutils, module-init-tools, initscripts >= 8.11.1-1, grubby >= 7.0.15-2.5
%if %{with_dracut}
%define initrd_prereq  dracut >= 004-336.27, grubby >= 7.0.10-1
%else
%define initrd_prereq  mkinitrd >= 6.0.91
%endif
# XXX: fedora16 has a prereq grubby >= 8.3-1

#
# This macro does requires, provides, conflicts, obsoletes for a kernel package.
#	%%kernel_reqprovconf <subpackage>
# It uses any kernel_<subpackage>_conflicts and kernel_<subpackage>_obsoletes
# macros defined above.
#
%define kernel_reqprovconf \
Provides: kernel = %{rpmversion}-%{pkg_release}\
Provides: kernel-%{_target_cpu} = %{rpmversion}-%{pkg_release}%{?1:.%{1}}\
Provides: kernel-drm = 4.3.0\
Provides: kernel-drm-nouveau = 16\
Provides: kernel-modeset = 1\
Provides: kernel-uname-r = %{KVERREL}%{?1:.%{1}}\
Requires(pre): %{kernel_prereq}\
Requires(pre): %{initrd_prereq}\
Requires(post): /sbin/new-kernel-pkg\
Requires(preun): /sbin/new-kernel-pkg\
Conflicts: %{kernel_dot_org_conflicts}\
Conflicts: %{package_conflicts}\
%{expand:%%{?kernel%{?1:_%{1}}_conflicts:Conflicts: %%{kernel%{?1:_%{1}}_conflicts}}}\
%{expand:%%{?kernel%{?1:_%{1}}_obsoletes:Obsoletes: %%{kernel%{?1:_%{1}}_obsoletes}}}\
%{expand:%%{?kernel%{?1:_%{1}}_provides:Provides: %%{kernel%{?1:_%{1}}_provides}}}\
# We can't let RPM do the dependencies automatic because it'll then pick up\
# a correct but undesirable perl dependency from the module headers which\
# isn't required for the kernel proper to function\
AutoReq: no\
AutoProv: yes\
%{nil}

Name: kernel%{?variant}
Group: System Environment/Kernel
License: GPLv2 and Redistributable, no modification permitted
URL: http://www.kernel.org/
Version: %{rpmversion}
Release: %{pkg_release}
# DO NOT CHANGE THE 'ExclusiveArch' LINE TO TEMPORARILY EXCLUDE AN ARCHITECTURE BUILD.
# SET %%nobuildarches (ABOVE) INSTEAD
ExclusiveArch: noarch %{all_x86} x86_64 %{arm}
ExclusiveOS: Linux

%kernel_reqprovconf
%ifarch x86_64
Requires(pre): microcode_ctl >= 2:2.1-47.36
%endif

%ifarch x86_64
Obsoletes: kernel-smp
%endif

%ifarch x86_64
Provides: kmod-lustre-client = 2.10.5
%endif


#
# List the packages used during the kernel build
#
BuildRequires: kmod >= 14, patch >= 2.5.4, bash >= 2.03, sh-utils, tar
BuildRequires: bzip2, findutils, gzip, m4, perl, make >= 3.78, diffutils, gawk
BuildRequires: gcc >= 7.2.1
# Required for kernel documentation build
BuildRequires: python-virtualenv, python-sphinx, ImageMagick-perl
#defines based on the compiler version we need to use
%global _gcc gcc
%global _gxx g++
%global _gccver %(eval %{_gcc} -dumpfullversion 2>/dev/null || :)
%if "%{_gccver}" > "7"
Provides: buildrequires(gcc) = %{_gccver}
%endif
BuildRequires: binutils >= 2.12
BuildRequires: system-rpm-config, gdb, bc
BuildRequires: net-tools
BuildRequires: xmlto, asciidoc
BuildRequires: openssl-devel
%if %{with_sparse}
BuildRequires: sparse >= 0.4.1
%endif
%if %{with_perf}
BuildRequires: elfutils-devel zlib-devel binutils-devel newt-devel perl(ExtUtils::Embed) bison
BuildRequires: audit-libs-devel
BuildRequires: numactl-devel
%if 0%{?sys_python_pkg:1}
BuildRequires: %{sys_python_pkg}-devel
%else
BuildRequires: python-devel
%endif

%endif
%if %{with_tools}
BuildRequires: pciutils-devel gettext
%endif # tools
BuildConflicts: rhbuildsys(DiskFree) < 3000Mb

%define fancy_debuginfo 0
%if %{with_debuginfo}
%define fancy_debuginfo 1
%endif

%if %{fancy_debuginfo}
# Fancy new debuginfo generation introduced in Fedora 8.
BuildRequires: rpm-build >= 4.4.2.1-4
## The -r flag to find-debuginfo.sh invokes eu-strip --reloc-debug-sections
## which reduces the number of relocations in kernel module .ko.debug files and
## was introduced with rpm 4.9 and elfutils 0.153.
#BuildRequires: rpm-build >= 4.9.0-1, elfutils >= elfutils-0.153-1
#%define debuginfo_args --strict-build-id -r
%define debuginfo_args --strict-build-id
%endif

%if %{signmodules}
BuildRequires: openssl
BuildRequires: pesign >= 0.10-4
%endif

Source0: linux-4.14.158.tar
Source1: linux-4.14.158-patches.tar

# this is for %{signmodules}
Source11: x509.genkey

Source15: kconfig.py
Source16: mod-extra.list
Source17: mod-extra.sh
Source18: mod-extra-sign.sh
%define modsign_cmd %{SOURCE18}

Source19: Makefile.config
Source20: config-generic
Source30: config-x86_32-generic
Source40: config-x86_64-generic
Source50: split-man.pl
%define split_man_cmd %{SOURCE50}

# Sources for kernel-tools
Source2000: cpupower.init
Source2001: cpupower.config

# __PATCHFILE_TEMPLATE__
Patch0001: 0001-kbuild-AFTER_LINK.patch
Patch0002: 0002-scsi-sd_revalidate_disk-prevent-NULL-ptr-deref.patch
Patch0003: 0003-bump-the-default-TTL-to-255.patch
Patch0004: 0004-bump-default-tcp_wmem-from-16KB-to-20KB.patch
Patch0005: 0005-force-perf-to-use-usr-bin-python-instead-of-usr-bin-.patch
Patch0006: 0006-nvme-update-timeout-module-parameter-type.patch
Patch0007: 0007-not-for-upstream-testmgr-config-changes-to-enable-FI.patch
Patch0008: 0008-drivers-introduce-AMAZON_DRIVER_UPDATES.patch
Patch0009: 0009-drivers-amazon-add-network-device-drivers-support.patch
Patch0010: 0010-drivers-amazon-introduce-AMAZON_ENA_ETHERNET.patch
Patch0011: 0011-Importing-Amazon-ENA-driver-1.5.0-into-amazon-4.14.y.patch
Patch0012: 0012-xen-manage-keep-track-of-the-on-going-suspend-mode.patch
Patch0013: 0013-xen-manage-introduce-helper-function-to-know-the-on-.patch
Patch0014: 0014-xenbus-add-freeze-thaw-restore-callbacks-support.patch
Patch0015: 0015-x86-xen-Introduce-new-function-to-map-HYPERVISOR_sha.patch
Patch0016: 0016-x86-xen-add-system-core-suspend-and-resume-callbacks.patch
Patch0017: 0017-xen-blkfront-add-callbacks-for-PM-suspend-and-hibern.patch
Patch0018: 0018-xen-netfront-add-callbacks-for-PM-suspend-and-hibern.patch
Patch0019: 0019-xen-time-introduce-xen_-save-restore-_steal_clock.patch
Patch0020: 0020-x86-xen-save-and-restore-steal-clock.patch
Patch0021: 0021-xen-events-add-xen_shutdown_pirqs-helper-function.patch
Patch0022: 0022-x86-xen-close-event-channels-for-PIRQs-in-system-cor.patch
Patch0023: 0023-PM-hibernate-update-the-resume-offset-on-SNAPSHOT_SE.patch
Patch0024: 0024-Not-for-upstream-PM-hibernate-Speed-up-hibernation-b.patch
Patch0025: 0025-xen-blkfront-resurrect-request-based-mode.patch
Patch0026: 0026-xen-blkfront-add-persistent_grants-parameter.patch
Patch0027: 0027-ACPI-SPCR-Make-SPCR-available-to-x86.patch
Patch0028: 0028-Revert-xen-dont-fiddle-with-event-channel-masking-in.patch
Patch0029: 0029-locking-paravirt-Use-new-static-key-for-controlling-.patch
Patch0030: 0030-KVM-Introduce-paravirtualization-hints-and-KVM_HINTS.patch
Patch0031: 0031-KVM-X86-Choose-qspinlock-when-dedicated-physical-CPU.patch
Patch0032: 0032-x86-paravirt-Set-up-the-virt_spin_lock_key-after-sta.patch
Patch0033: 0033-KVM-X86-Fix-setup-the-virt_spin_lock_key-before-stat.patch
Patch0034: 0034-xen-blkfront-Fixed-blkfront_restore-to-remove-a-call.patch
Patch0035: 0035-x86-tsc-avoid-system-instability-in-hibernation.patch
Patch0036: 0036-blk-mq-simplify-queue-mapping-schedule-with-each-pos.patch
Patch0037: 0037-blk-wbt-Avoid-lock-contention-and-thundering-herd-is.patch
Patch0038: 0038-x86-MCE-AMD-Read-MCx_MISC-block-addresses-on-any-CPU.patch
Patch0039: 0039-x86-CPU-Rename-intel_cacheinfo.c-to-cacheinfo.c.patch
Patch0040: 0040-x86-CPU-AMD-Calculate-last-level-cache-ID-from-numbe.patch
Patch0041: 0041-x86-CPU-AMD-Fix-LLC-ID-bit-shift-calculation.patch
Patch0042: 0042-sched-topology-Introduce-NUMA-identity-node-sched-do.patch
Patch0043: 0043-x86-CPU-AMD-Derive-CPU-topology-from-CPUID-function-.patch
Patch0044: 0044-vmxnet3-increase-default-rx-ring-sizes.patch
Patch0045: 0045-block-xen-blkfront-consider-new-dom0-features-on-res.patch
Patch0046: 0046-ACPICA-Enable-sleep-button-on-ACPI-legacy-wake.patch
Patch0047: 0047-xen-restore-pirqs-on-resume-from-hibernation.patch
Patch0048: 0048-xen-Only-restore-the-ACPI-SCI-interrupt-in-xen_resto.patch
Patch0049: 0049-net-ena-Import-the-ENA-v2-driver-2.0.2g.patch
Patch0050: 0050-arm64-export-memblock_reserve-d-regions-via-proc-iom.patch
Patch0051: 0051-arm64-Fix-proc-iomem-for-reserved-but-not-memory-reg.patch
Patch0052: 0052-efi-arm64-Check-whether-x18-is-preserved-by-runtime-.patch
Patch0053: 0053-arm64-kexec-always-reset-to-EL2-if-present.patch
Patch0054: 0054-arm64-acpi-fix-alignment-fault-in-accessing-ACPI.patch
Patch0055: 0055-ACPICA-ACPI-6.2-Additional-PPTT-flags.patch
Patch0056: 0056-drivers-base-cacheinfo-move-cache_setup_of_node.patch
Patch0057: 0057-drivers-base-cacheinfo-setup-DT-cache-properties-ear.patch
Patch0058: 0058-cacheinfo-rename-of_node-to-fw_token.patch
Patch0059: 0059-arm64-acpi-Create-arch-specific-cpu-to-acpi-id-helpe.patch
Patch0060: 0060-ACPI-PPTT-Add-Processor-Properties-Topology-Table-pa.patch
Patch0061: 0061-ACPI-Enable-PPTT-support-on-ARM64.patch
Patch0062: 0062-drivers-base-cacheinfo-Add-support-for-ACPI-based-fi.patch
Patch0063: 0063-arm64-Add-support-for-ACPI-based-firmware-tables.patch
Patch0064: 0064-arm64-topology-rename-cluster_id.patch
Patch0065: 0065-arm64-topology-enable-ACPI-PPTT-based-CPU-topology.patch
Patch0066: 0066-ACPI-Add-PPTT-to-injectable-table-list.patch
Patch0067: 0067-arm64-topology-divorce-MC-scheduling-domain-from-cor.patch
Patch0068: 0068-ACPI-PPTT-use-ACPI-ID-whenever-ACPI_PPTT_ACPI_PROCES.patch
Patch0069: 0069-ACPI-PPTT-fix-build-when-CONFIG_ACPI_PPTT-is-not-ena.patch
Patch0070: 0070-ACPI-PPTT-Handle-architecturally-unknown-cache-types.patch
Patch0071: 0071-xen-netfront-call-netif_device_attach-on-resume.patch
Patch0072: 0072-xfs-refactor-superblock-verifiers.patch
Patch0073: 0073-libxfs-add-more-bounds-checking-to-sb-sanity-checks.patch
Patch0074: 0074-xfs-only-validate-summary-counts-on-primary-superblo.patch
Patch0075: 0075-xfs-iomap-define-and-use-the-IOMAP_F_DIRTY-flag-in-x.patch
Patch0076: 0076-iomap-add-a-swapfile-activation-function.patch
Patch0077: 0077-iomap-provide-more-useful-errors-for-invalid-swap-fi.patch
Patch0078: 0078-iomap-don-t-allow-holes-in-swapfiles.patch
Patch0079: 0079-iomap-inline-data-should-be-an-iomap-type-not-a-flag.patch
Patch0080: 0080-iomap-fsync-swap-files-before-iterating-mappings.patch
Patch0081: 0081-Import-lustre-client-2.10.5.patch
Patch0082: 0082-Config-glue-for-lustre-client.patch
Patch0083: 0083-net-allow-per-netns-sysctl_rmem-and-sysctl_wmem-for-.patch
Patch0084: 0084-tcp-Namespace-ify-sysctl_tcp_rmem-and-sysctl_tcp_wme.patch
Patch0085: 0085-Add-new-config-CONFIG_MICROVM-to-enable-microvm-opti.patch
Patch0086: 0086-x86-stacktrace-Do-not-unwind-after-user-regs.patch
Patch0087: 0087-x86-stacktrace-Remove-STACKTRACE_DUMP_ONCE.patch
Patch0088: 0088-x86-stacktrace-Clarify-the-reliable-success-paths.patch
Patch0089: 0089-x86-stacktrace-Do-not-fail-for-ORC-with-regs-on-stac.patch
Patch0090: 0090-x86-unwind-orc-Detect-the-end-of-the-stack.patch
Patch0091: 0091-x86-stacktrace-Enable-HAVE_RELIABLE_STACKTRACE-for-t.patch
Patch0092: 0092-lustre-fix-ACL-handling.patch
Patch0093: 0093-irqchip-gic-v2m-invoke-from-gic-v3-initialization-an.patch
Patch0094: 0094-PCI-al-Add-Amazon-Annapurna-Labs-PCIe-host-controlle.patch
Patch0095: 0095-arm64-acpi-pci-invoke-_DSM-whether-to-preserve-firmw.patch
Patch0096: 0096-NFS-Remove-redundant-semicolon.patch
Patch0097: 0097-Fix-microvm-config-dependency-in-Kconfig.patch
Patch0098: 0098-microvm-enable-debug-in-case-of-tcp-out-of-memory.patch
Patch0099: 0099-linux-ena-update-ENA-linux-driver-to-version-2.1.1.patch
Patch0100: 0100-PCI-Add-Amazon-s-Annapurna-Labs-vendor-ID.patch
Patch0101: 0101-PCI-Add-ACS-quirk-for-Amazon-Annapurna-Labs-root-por.patch
Patch0102: 0102-Partially-revert-cc946adcb9e983ad9fe56ebe35f1292e111.patch
Patch0103: 0103-livepatch-introduce-shadow-variable-API.patch
Patch0104: 0104-livepatch-__klp_shadow_get_or_alloc-is-local-to-shad.patch
Patch0105: 0105-livepatch-add-un-patch-callbacks.patch
Patch0106: 0106-livepatch-move-transition-complete-notice-into-klp_c.patch
Patch0107: 0107-livepatch-add-transition-notices.patch
Patch0108: 0108-livepatch-Correctly-call-klp_post_unpatch_callback-i.patch
Patch0109: 0109-livepatch-__klp_disable_patch-should-never-be-called.patch
Patch0110: 0110-livepatch-send-a-fake-signal-to-all-blocking-tasks.patch
Patch0111: 0111-livepatch-force-transition-to-finish.patch
Patch0112: 0112-livepatch-Remove-immediate-feature.patch
Patch0113: 0113-livepatch-add-locking-to-force-and-signal-functions.patch
Patch0114: 0114-livepatch-Initialize-shadow-variables-safely-by-a-cu.patch
Patch0115: 0115-livepatch-Allow-to-call-a-custom-callback-when-freei.patch
Patch0116: 0116-livepatch-Remove-reliable-stacktrace-check-in-klp_tr.patch
Patch0117: 0117-livepatch-Replace-synchronize_sched-with-synchronize.patch
Patch0118: 0118-livepatch-Change-unsigned-long-old_addr-void-old_fun.patch
Patch0119: 0119-xen-Restore-xen-pirqs-on-resume-from-hibernation.patch
Patch0120: 0120-block-add-io-timeout-to-sysfs.patch
Patch0121: 0121-block-don-t-show-io_timeout-if-driver-has-no-timeout.patch
Patch0122: 0122-Add-Amazon-EFA-driver-version-1.4.patch
Patch0123: 0123-percpu-refcount-Introduce-percpu_ref_resurrect.patch
Patch0124: 0124-block-Allow-unfreezing-of-a-queue-while-requests-are.patch
Patch0125: 0125-nvme-change-namespaces_mutext-to-namespaces_rwsem.patch
Patch0126: 0126-blk-mq-fix-hang-caused-by-freeze-unfreeze-sequence.patch
Patch0127: 0127-nvme-move-the-dying-queue-check-from-cancel-to-compl.patch
Patch0128: 0128-nvme-pci-Better-support-for-disabling-controller.patch
Patch0129: 0129-nvme-host-core-Allow-overriding-of-wait_ready-timeou.patch
Patch0130: 0130-nvme-host-pci-Fix-a-race-in-controller-removal.patch
Patch0131: 0131-nvme-pci-move-cq_vector-1-check-outside-of-q_lock.patch
Patch0132: 0132-irqchip-gic-v3-its-Pass-its_node-pointer-to-each-com.patch
Patch0133: 0133-irqchip-gic-v3-its-Only-emit-SYNC-if-targetting-a-va.patch
Patch0134: 0134-irqchip-gic-v3-its-Only-emit-VSYNC-if-targetting-a-v.patch
Patch0135: 0135-irqchip-gic-v3-its-Refactor-LPI-allocator.patch
Patch0136: 0136-irqchip-gic-v3-its-Use-full-range-of-LPIs.patch
Patch0137: 0137-irqchip-gic-v3-its-Move-minimum-LPI-requirements-to-.patch
Patch0138: 0138-irqchip-gic-v3-its-Drop-chunk-allocation-compatibili.patch
Patch0139: 0139-irqchip-gic-v3-Expose-GICD_TYPER-in-the-rdist-struct.patch
Patch0140: 0140-irqchip-gic-v3-its-Honor-hypervisor-enforced-LPI-ran.patch
Patch0141: 0141-irqchip-gic-v3-its-Reduce-minimum-LPI-allocation-to-.patch
Patch0142: 0142-irqchip-gic-v3-its-Cap-lpi_id_bits-to-reduce-memory-.patch
Patch0143: 0143-irqchip-gic-v3-its-Gracefully-fail-on-LPI-exhaustion.patch
Patch0144: 0144-irqchip-gic-v3-its-Fix-comparison-logic-in-lpi_range.patch
Patch0145: 0145-iommu-io-pgtable-arm-Convert-to-IOMMU-API-TLB-sync.patch
Patch0146: 0146-iommu-io-pgtable-arm-v7s-Convert-to-IOMMU-API-TLB-sy.patch
Patch0147: 0147-iommu-arm-smmu-v3-Implement-flush_iotlb_all-hook.patch
Patch0148: 0148-iommu-dma-Add-support-for-non-strict-mode.patch
Patch0149: 0149-iommu-Add-iommu.strict-command-line-option.patch
Patch0150: 0150-iommu-io-pgtable-arm-Add-support-for-non-strict-mode.patch
Patch0151: 0151-iommu-arm-smmu-v3-Add-support-for-non-strict-mode.patch
Patch0152: 0152-iommu-io-pgtable-arm-v7s-Add-support-for-non-strict-.patch
Patch0153: 0153-iommu-arm-smmu-Support-non-strict-mode.patch
Patch0154: 0154-iommu-use-config-option-to-specify-if-iommu-mode-sho.patch
Patch0155: 0155-locking-atomic-Add-atomic_cond_read_acquire.patch
Patch0156: 0156-locking-barriers-Introduce-smp_cond_load_relaxed-and.patch
Patch0157: 0157-locking-qspinlock-Use-atomic_cond_read_acquire.patch
Patch0158: 0158-locking-mcs-Use-smp_cond_load_acquire-in-MCS-spin-lo.patch
Patch0159: 0159-locking-qspinlock-Use-smp_cond_load_relaxed-to-wait-.patch
Patch0160: 0160-locking-qspinlock-Use-smp_store_release-in-queued_sp.patch
Patch0161: 0161-locking-qspinlock-Elide-back-to-back-RELEASE-operati.patch
Patch0162: 0162-locking-qspinlock-Use-try_cmpxchg-instead-of-cmpxchg.patch
Patch0163: 0163-MAINTAINERS-Add-myself-as-a-co-maintainer-for-the-lo.patch
Patch0164: 0164-arm64-barrier-Implement-smp_cond_load_relaxed.patch
Patch0165: 0165-arm64-locking-Replace-ticket-lock-implementation-wit.patch
Patch0166: 0166-arm64-kconfig-Ensure-spinlock-fastpaths-are-inlined-.patch
Patch0167: 0167-arm64-pull-in-upstream-erratum-workarounds.patch
Patch0168: 0168-arm64-Avoid-flush_icache_range-in-alternatives-patch.patch
Patch0169: 0169-update-ena-driver-to-version-2.1.3.patch
Patch0170: 0170-Revert-nvme-pci-Better-support-for-disabling-control.patch
Patch0171: 0171-nvme-pci-introduce-RECONNECTING-state-to-mark-initia.patch
Patch0172: 0172-nvme-allow-controller-RESETTING-to-RECONNECTING-tran.patch
Patch0173: 0173-nvme-rename-NVME_CTRL_RECONNECTING-state-to-NVME_CTR.patch
Patch0174: 0174-nvme-pci-Fix-timeouts-in-connecting-state.patch
Patch0175: 0175-nvme-pci-shutdown-on-timeout-during-deletion.patch
Patch0176: 0176-nvme-pci-Unblock-reset_work-on-IO-failure.patch
Patch0177: 0177-nvme-pci-Don-t-disable-on-timeout-in-reset-state.patch
Patch0178: 0178-nvme-pci-use-atomic-bitops-to-mark-a-queue-enabled.patch
Patch0179: 0179-arm64-fix-merge-error-in-errata-changes.patch
Patch0180: 0180-lustre-hold-lock-while-walking-changelog-dev-list.patch
Patch0181: 0181-Revert-Fix-the-locking-in-dcache_readdir-and-friends.patch
Patch0182: 0182-drivers-amazon-efa-update-to-1.5.0.patch
Patch0183: 0183-SMB3-Backup-intent-flag-missing-from-compounded-ops.patch
Patch0184: 0184-Add-support-for-setting-owner-info-dos-attributes-an.patch

BuildRoot: %{_tmppath}/kernel-%{KVERREL}-root

%description
The kernel package contains the Linux kernel (vmlinuz), the core of any
Linux operating system.  The kernel handles the basic functions
of the operating system: memory allocation, process allocation, device
input and output, etc.


%package doc
Summary: Various documentation bits found in the kernel source
Group: Documentation
%description doc
This package contains documentation files from the kernel
source. Various bits of information about the Linux kernel and the
device drivers shipped with it are documented in these files.

You'll want to install this package if you need a reference to the
options that can be passed to Linux kernel modules at load time.


%package headers
Summary: Header files for the Linux kernel for use by glibc
Group: Development/System
Obsoletes: glibc-kernheaders
Provides: glibc-kernheaders = 3.0-46
%description headers
Kernel-headers includes the C header files that specify the interface
between the Linux kernel and userspace libraries and programs.  The
header files define structures and constants that are needed for
building most standard programs and are also needed for rebuilding the
glibc package.

%package debuginfo-common-%{_target_cpu}
Summary: Kernel source files used by %{name}-debuginfo packages
Group: Development/Debug
%description debuginfo-common-%{_target_cpu}
This package is required by %{name}-debuginfo subpackages.
It provides the kernel source files common to all builds.

%if %{with_perf}
%package -n perf
Summary: Performance monitoring for the Linux kernel
Group: Development/System
License: GPLv2
%description -n perf
This package contains the perf tool, which enables performance monitoring
of the Linux kernel.

%package -n perf-debuginfo
Summary: Debug information for package perf
Group: Development/Debug
Requires: %{name}-debuginfo-common-%{_target_cpu} = %{version}-%{release}
AutoReqProv: no
%description -n perf-debuginfo
This package provides debug information for the perf package.

# Note that this pattern only works right to match the .build-id
# symlinks because of the trailing nonmatching alternation and
# the leading .*, because of find-debuginfo.sh's buggy handling
# of matching the pattern against the symlinks file.
%{expand:%%global debuginfo_args %{?debuginfo_args} -p '.*%%{_bindir}/perf(\.debug)?|.*%%{_libexecdir}/perf-core/.*|.*%%{python_sitearch}/perf.so(\.debug)?|.*%%{_libdir}/traceevent/plugins/.*|XXX' -o perf-debuginfo.list}
%endif #perf

%if %{with_tools}
%package tools
Summary: Assortment of tools for the Linux kernel
Group: Development/System
License: GPLv2
Provides:  cpupowerutils = 1:009-0.6.p1
Obsoletes: cpupowerutils < 1:009-0.6.p1
Provides:  cpufreq-utils = 1:009-0.6.p1
Provides:  cpufrequtils = 1:009-0.6.p1
Obsoletes: cpufreq-utils < 1:009-0.6.p1
Obsoletes: cpufrequtils < 1:009-0.6.p1
Obsoletes: cpuspeed < 1:1.5-16

%description tools
This package contains the tools/ directory from the kernel source
and the supporting documentation.

%package tools-devel
Summary: Assortment of tools for the Linux kernel
Group: Development/System
License: GPLv2
Requires: kernel-tools = %{version}-%{release}
%ifarch %{cpupowerarchs}
Provides:  cpupowerutils-devel = 1:009-0.6.p1
Obsoletes: cpupowerutils-devel < 1:009-0.6.p1
%endif # cpupower

%description tools-devel
This package contains the development files for the tools/ directory from
the kernel source.

%package tools-debuginfo
Summary: Debug information for package kernel-tools
Group: Development/Debug
Requires: %{name}-debuginfo-common-%{_target_cpu} = %{version}-%{release}
AutoReqProv: no
%description tools-debuginfo
This package provides debug information for package kernel-tools.

# Note that this pattern only works right to match the .build-id
# symlinks because of the trailing nonmatching alternation and
# the leading .*, because of find-debuginfo.sh's buggy handling
# of matching the pattern against the symlinks file.
%{expand:%%global debuginfo_args %{?debuginfo_args} -p '.*%%{_bindir}/centrino-decode(\.debug)?|.*%%{_bindir}/powernow-k8-decode(\.debug)?|.*%%{_bindir}/cpupower(\.debug)?|.*%%{_libdir}/libcpupower.*|XXX' -o kernel-tools-debuginfo.list}
%endif

#
# This macro creates a kernel-<subpackage>-debuginfo package.
#	%%kernel_debuginfo_package <subpackage>
#
%define kernel_debuginfo_package() \
%package %{?1:%{1}-}debuginfo\
Summary: Debug information for package %{name}%{?1:-%{1}}\
Group: Development/Debug\
Requires: %{name}-debuginfo-common-%{_target_cpu} = %{version}-%{release}\
Provides: %{name}%{?1:-%{1}}-debuginfo-%{_target_cpu} = %{version}-%{release}\
AutoReqProv: no\
%description -n %{name}%{?1:-%{1}}-debuginfo\
This package provides debug information for package %{name}%{?1:-%{1}}.\
This is required to use SystemTap with %{name}%{?1:-%{1}}-%{KVERREL}.\
%{expand:%%global debuginfo_args %{?debuginfo_args} -p '/.*/%%{KVERREL}%{?1:\.%{1}}/.*|/.*%%{KVERREL}%{?1:\.%{1}}(\.debug)?' -o debuginfo%{?1}.list}\
%{nil}

#
# This macro creates a kernel-<subpackage>-devel package.
#	%%kernel_devel_package <subpackage> <pretty-name>
#
%define kernel_devel_package() \
%package %{?1:%{1}-}devel\
Summary: Development package for building kernel modules to match the %{?2:%{2} }kernel\
Group: System Environment/Kernel\
Provides: kernel%{?1:-%{1}}-devel-%{_target_cpu} = %{version}-%{release}\
Provides: kernel-devel-%{_target_cpu} = %{version}-%{release}%{?1:.%{1}}\
Provides: kernel-devel = %{version}-%{release}%{?1:.%{1}}\
Provides: kernel-devel-uname-r = %{KVERREL}%{?1:.%{1}}\
AutoReqProv: no\
Requires(pre): /usr/bin/find\
Requires(post): /usr/sbin/hardlink\
Requires: perl\
Requires: elfutils-libelf-devel\
Requires: gcc >= 7.2.1\
%if  "%{_gccver}" > "7"\
Provides: buildrequires(gcc) = %{_gccver}\
%endif\
%description -n kernel%{?variant}%{?1:-%{1}}-devel\
This package provides kernel headers and makefiles sufficient to build modules\
against the %{?2:%{2} }kernel package.\
%{nil}

#
# This macro creates a kernel-<subpackage> and its -devel and -debuginfo too.
#	%%define variant_summary The Linux kernel compiled for <configuration>
#	%%kernel_variant_package [-n <pretty-name>] <subpackage>
#
%define kernel_variant_package(n:) \
%package %1\
Summary: %{variant_summary}\
Group: System Environment/Kernel\
%kernel_reqprovconf\
%{expand:%%kernel_devel_package %1 %{!?-n:%1}%{?-n:%{-n*}}}\
%{expand:%%kernel_debuginfo_package %1}\
%{nil}


# First the auxiliary packages of the main kernel package.
%kernel_devel_package
%kernel_debuginfo_package


# Now, each variant package.

%define variant_summary The Linux kernel compiled with extra debugging enabled
%kernel_variant_package debug
%description debug
The kernel package contains the Linux kernel (vmlinuz), the core of any
Linux operating system.  The kernel handles the basic functions
of the operating system:  memory allocation, process allocation, device
input and output, etc.

This variant of the kernel has numerous debugging options enabled.
It should only be installed when trying to gather additional information
on kernel bugs, as some of these options impact performance noticably.


%prep
# more sanity checking; do it quietly
if [ "%{patches}" != "%%{patches}" ] ; then
  for patch in %{patches} ; do
    if [ ! -f $patch ] ; then
      echo "ERROR: Patch  ${patch##/*/}  listed in specfile but is missing"
      exit 1
    fi
  done
fi 2>/dev/null

patch_command='patch -p1 -F1 -s'

ApplyNoCheckPatch()
{
  local patch=$1
  shift
  case "$patch" in
    *.bz2) bunzip2 < "$RPM_SOURCE_DIR/$patch" | $patch_command ${1+"$@"} ;;
    *.gz) gunzip < "$RPM_SOURCE_DIR/$patch" | $patch_command ${1+"$@"} ;;
    *) $patch_command ${1+"$@"} < $patch ;;
  esac
}

ApplyPatch()
{
  local patch=$1
  shift
  if [ ! -f $RPM_SOURCE_DIR/$patch ]; then
    exit 1
  fi
  if ! grep -E "^Patch[0-9]+: $patch\$" %{_specdir}/${RPM_PACKAGE_NAME%%%%%{?variant}}.spec ; then
    if [ "${patch:0:8}" != "patch-3." ] ; then
      echo "ERROR: Patch  $patch  not listed as a source patch in specfile"
      exit 1
    fi
  fi 2>/dev/null
  case "$patch" in
  *.bz2) bunzip2 < "$RPM_SOURCE_DIR/$patch" | $patch_command ${1+"$@"} ;;
  *.gz) gunzip < "$RPM_SOURCE_DIR/$patch" | $patch_command ${1+"$@"} ;;
  *) $patch_command ${1+"$@"} < "$RPM_SOURCE_DIR/$patch" ;;
  esac
}

# don't apply patch if it's empty
ApplyOptionalPatch()
{
  local patch=$1
  shift
  if [ ! -f $RPM_SOURCE_DIR/$patch ]; then
    exit 1
  fi
  local C=$(wc -l $RPM_SOURCE_DIR/$patch | awk '{print $1}')
  if [ "$C" -gt 9 ]; then
    ApplyPatch $patch ${1+"$@"}
  fi
}

# First we unpack the kernel tarball.
# If this isn't the first make prep, we use links to the existing clean tarball
# which speeds things up quite a bit.

# Update to latest upstream.
%define vanillaversion %{kversion}

# %%{vanillaversion} : the full version name, e.g. 2.6.35-rc6-git3
# %%{kversion}       : the base version, e.g. 2.6.34

# Use kernel-%%{kversion}%%{?dist} as the top-level directory name
# so we can prep different trees within a single git directory.

%setup -q -n kernel-%{kversion}%{?dist} -c
mv linux-%{vanillaversion} vanilla-%{vanillaversion}

%if "%{kversion}" != "%{vanillaversion}"
# Need to apply patches to the base vanilla version.
pushd vanilla-%{vanillaversion} && popd

%endif

# Now build the fedora kernel tree.
if [ -d linux-%{KVERREL} ]; then
  # Just in case we ctrl-c'd a prep already
  rm -rf deleteme.%{_target_cpu}
  # Move away the stale away, and delete in background.
  mv linux-%{KVERREL} deleteme.%{_target_cpu}
  rm -rf deleteme.%{_target_cpu} &
fi

cp -rl vanilla-%{vanillaversion} linux-%{KVERREL}

cd linux-%{KVERREL}
tar xf %{SOURCE1}

# Drop some necessary files from the source dir into the buildroot
cp $RPM_SOURCE_DIR/config-* .
cp %{SOURCE15} .

# Dynamically generate kernel .config files from config-* files
make -f %{SOURCE19} VERSION=%{version} config

# apply the patches we had included in the -patches tarball. We use the
# linux-KVER-patches.list hardcoded apply log filename
patch_list=linux-%{kversion}-patches.list
if [ ! -f ${patch_list} ] ; then
    echo "ERROR: patch file apply log is missing: ${patch_list} not found"
    exit -1
fi
for p in `cat $patch_list` ; do
  ApplyNoCheckPatch ${p}
done

# __APPLYFILE_TEMPLATE__
ApplyPatch 0001-kbuild-AFTER_LINK.patch
ApplyPatch 0002-scsi-sd_revalidate_disk-prevent-NULL-ptr-deref.patch
ApplyPatch 0003-bump-the-default-TTL-to-255.patch
ApplyPatch 0004-bump-default-tcp_wmem-from-16KB-to-20KB.patch
ApplyPatch 0005-force-perf-to-use-usr-bin-python-instead-of-usr-bin-.patch
ApplyPatch 0006-nvme-update-timeout-module-parameter-type.patch
ApplyPatch 0007-not-for-upstream-testmgr-config-changes-to-enable-FI.patch
ApplyPatch 0008-drivers-introduce-AMAZON_DRIVER_UPDATES.patch
ApplyPatch 0009-drivers-amazon-add-network-device-drivers-support.patch
ApplyPatch 0010-drivers-amazon-introduce-AMAZON_ENA_ETHERNET.patch
ApplyPatch 0011-Importing-Amazon-ENA-driver-1.5.0-into-amazon-4.14.y.patch
ApplyPatch 0012-xen-manage-keep-track-of-the-on-going-suspend-mode.patch
ApplyPatch 0013-xen-manage-introduce-helper-function-to-know-the-on-.patch
ApplyPatch 0014-xenbus-add-freeze-thaw-restore-callbacks-support.patch
ApplyPatch 0015-x86-xen-Introduce-new-function-to-map-HYPERVISOR_sha.patch
ApplyPatch 0016-x86-xen-add-system-core-suspend-and-resume-callbacks.patch
ApplyPatch 0017-xen-blkfront-add-callbacks-for-PM-suspend-and-hibern.patch
ApplyPatch 0018-xen-netfront-add-callbacks-for-PM-suspend-and-hibern.patch
ApplyPatch 0019-xen-time-introduce-xen_-save-restore-_steal_clock.patch
ApplyPatch 0020-x86-xen-save-and-restore-steal-clock.patch
ApplyPatch 0021-xen-events-add-xen_shutdown_pirqs-helper-function.patch
ApplyPatch 0022-x86-xen-close-event-channels-for-PIRQs-in-system-cor.patch
ApplyPatch 0023-PM-hibernate-update-the-resume-offset-on-SNAPSHOT_SE.patch
ApplyPatch 0024-Not-for-upstream-PM-hibernate-Speed-up-hibernation-b.patch
ApplyPatch 0025-xen-blkfront-resurrect-request-based-mode.patch
ApplyPatch 0026-xen-blkfront-add-persistent_grants-parameter.patch
ApplyPatch 0027-ACPI-SPCR-Make-SPCR-available-to-x86.patch
ApplyPatch 0028-Revert-xen-dont-fiddle-with-event-channel-masking-in.patch
ApplyPatch 0029-locking-paravirt-Use-new-static-key-for-controlling-.patch
ApplyPatch 0030-KVM-Introduce-paravirtualization-hints-and-KVM_HINTS.patch
ApplyPatch 0031-KVM-X86-Choose-qspinlock-when-dedicated-physical-CPU.patch
ApplyPatch 0032-x86-paravirt-Set-up-the-virt_spin_lock_key-after-sta.patch
ApplyPatch 0033-KVM-X86-Fix-setup-the-virt_spin_lock_key-before-stat.patch
ApplyPatch 0034-xen-blkfront-Fixed-blkfront_restore-to-remove-a-call.patch
ApplyPatch 0035-x86-tsc-avoid-system-instability-in-hibernation.patch
ApplyPatch 0036-blk-mq-simplify-queue-mapping-schedule-with-each-pos.patch
ApplyPatch 0037-blk-wbt-Avoid-lock-contention-and-thundering-herd-is.patch
ApplyPatch 0038-x86-MCE-AMD-Read-MCx_MISC-block-addresses-on-any-CPU.patch
ApplyPatch 0039-x86-CPU-Rename-intel_cacheinfo.c-to-cacheinfo.c.patch
ApplyPatch 0040-x86-CPU-AMD-Calculate-last-level-cache-ID-from-numbe.patch
ApplyPatch 0041-x86-CPU-AMD-Fix-LLC-ID-bit-shift-calculation.patch
ApplyPatch 0042-sched-topology-Introduce-NUMA-identity-node-sched-do.patch
ApplyPatch 0043-x86-CPU-AMD-Derive-CPU-topology-from-CPUID-function-.patch
ApplyPatch 0044-vmxnet3-increase-default-rx-ring-sizes.patch
ApplyPatch 0045-block-xen-blkfront-consider-new-dom0-features-on-res.patch
ApplyPatch 0046-ACPICA-Enable-sleep-button-on-ACPI-legacy-wake.patch
ApplyPatch 0047-xen-restore-pirqs-on-resume-from-hibernation.patch
ApplyPatch 0048-xen-Only-restore-the-ACPI-SCI-interrupt-in-xen_resto.patch
ApplyPatch 0049-net-ena-Import-the-ENA-v2-driver-2.0.2g.patch
ApplyPatch 0050-arm64-export-memblock_reserve-d-regions-via-proc-iom.patch
ApplyPatch 0051-arm64-Fix-proc-iomem-for-reserved-but-not-memory-reg.patch
ApplyPatch 0052-efi-arm64-Check-whether-x18-is-preserved-by-runtime-.patch
ApplyPatch 0053-arm64-kexec-always-reset-to-EL2-if-present.patch
ApplyPatch 0054-arm64-acpi-fix-alignment-fault-in-accessing-ACPI.patch
ApplyPatch 0055-ACPICA-ACPI-6.2-Additional-PPTT-flags.patch
ApplyPatch 0056-drivers-base-cacheinfo-move-cache_setup_of_node.patch
ApplyPatch 0057-drivers-base-cacheinfo-setup-DT-cache-properties-ear.patch
ApplyPatch 0058-cacheinfo-rename-of_node-to-fw_token.patch
ApplyPatch 0059-arm64-acpi-Create-arch-specific-cpu-to-acpi-id-helpe.patch
ApplyPatch 0060-ACPI-PPTT-Add-Processor-Properties-Topology-Table-pa.patch
ApplyPatch 0061-ACPI-Enable-PPTT-support-on-ARM64.patch
ApplyPatch 0062-drivers-base-cacheinfo-Add-support-for-ACPI-based-fi.patch
ApplyPatch 0063-arm64-Add-support-for-ACPI-based-firmware-tables.patch
ApplyPatch 0064-arm64-topology-rename-cluster_id.patch
ApplyPatch 0065-arm64-topology-enable-ACPI-PPTT-based-CPU-topology.patch
ApplyPatch 0066-ACPI-Add-PPTT-to-injectable-table-list.patch
ApplyPatch 0067-arm64-topology-divorce-MC-scheduling-domain-from-cor.patch
ApplyPatch 0068-ACPI-PPTT-use-ACPI-ID-whenever-ACPI_PPTT_ACPI_PROCES.patch
ApplyPatch 0069-ACPI-PPTT-fix-build-when-CONFIG_ACPI_PPTT-is-not-ena.patch
ApplyPatch 0070-ACPI-PPTT-Handle-architecturally-unknown-cache-types.patch
ApplyPatch 0071-xen-netfront-call-netif_device_attach-on-resume.patch
ApplyPatch 0072-xfs-refactor-superblock-verifiers.patch
ApplyPatch 0073-libxfs-add-more-bounds-checking-to-sb-sanity-checks.patch
ApplyPatch 0074-xfs-only-validate-summary-counts-on-primary-superblo.patch
ApplyPatch 0075-xfs-iomap-define-and-use-the-IOMAP_F_DIRTY-flag-in-x.patch
ApplyPatch 0076-iomap-add-a-swapfile-activation-function.patch
ApplyPatch 0077-iomap-provide-more-useful-errors-for-invalid-swap-fi.patch
ApplyPatch 0078-iomap-don-t-allow-holes-in-swapfiles.patch
ApplyPatch 0079-iomap-inline-data-should-be-an-iomap-type-not-a-flag.patch
ApplyPatch 0080-iomap-fsync-swap-files-before-iterating-mappings.patch
ApplyPatch 0081-Import-lustre-client-2.10.5.patch
ApplyPatch 0082-Config-glue-for-lustre-client.patch
ApplyPatch 0083-net-allow-per-netns-sysctl_rmem-and-sysctl_wmem-for-.patch
ApplyPatch 0084-tcp-Namespace-ify-sysctl_tcp_rmem-and-sysctl_tcp_wme.patch
ApplyPatch 0085-Add-new-config-CONFIG_MICROVM-to-enable-microvm-opti.patch
ApplyPatch 0086-x86-stacktrace-Do-not-unwind-after-user-regs.patch
ApplyPatch 0087-x86-stacktrace-Remove-STACKTRACE_DUMP_ONCE.patch
ApplyPatch 0088-x86-stacktrace-Clarify-the-reliable-success-paths.patch
ApplyPatch 0089-x86-stacktrace-Do-not-fail-for-ORC-with-regs-on-stac.patch
ApplyPatch 0090-x86-unwind-orc-Detect-the-end-of-the-stack.patch
ApplyPatch 0091-x86-stacktrace-Enable-HAVE_RELIABLE_STACKTRACE-for-t.patch
ApplyPatch 0092-lustre-fix-ACL-handling.patch
ApplyPatch 0093-irqchip-gic-v2m-invoke-from-gic-v3-initialization-an.patch
ApplyPatch 0094-PCI-al-Add-Amazon-Annapurna-Labs-PCIe-host-controlle.patch
ApplyPatch 0095-arm64-acpi-pci-invoke-_DSM-whether-to-preserve-firmw.patch
ApplyPatch 0096-NFS-Remove-redundant-semicolon.patch
ApplyPatch 0097-Fix-microvm-config-dependency-in-Kconfig.patch
ApplyPatch 0098-microvm-enable-debug-in-case-of-tcp-out-of-memory.patch
ApplyPatch 0099-linux-ena-update-ENA-linux-driver-to-version-2.1.1.patch
ApplyPatch 0100-PCI-Add-Amazon-s-Annapurna-Labs-vendor-ID.patch
ApplyPatch 0101-PCI-Add-ACS-quirk-for-Amazon-Annapurna-Labs-root-por.patch
ApplyPatch 0102-Partially-revert-cc946adcb9e983ad9fe56ebe35f1292e111.patch
ApplyPatch 0103-livepatch-introduce-shadow-variable-API.patch
ApplyPatch 0104-livepatch-__klp_shadow_get_or_alloc-is-local-to-shad.patch
ApplyPatch 0105-livepatch-add-un-patch-callbacks.patch
ApplyPatch 0106-livepatch-move-transition-complete-notice-into-klp_c.patch
ApplyPatch 0107-livepatch-add-transition-notices.patch
ApplyPatch 0108-livepatch-Correctly-call-klp_post_unpatch_callback-i.patch
ApplyPatch 0109-livepatch-__klp_disable_patch-should-never-be-called.patch
ApplyPatch 0110-livepatch-send-a-fake-signal-to-all-blocking-tasks.patch
ApplyPatch 0111-livepatch-force-transition-to-finish.patch
ApplyPatch 0112-livepatch-Remove-immediate-feature.patch
ApplyPatch 0113-livepatch-add-locking-to-force-and-signal-functions.patch
ApplyPatch 0114-livepatch-Initialize-shadow-variables-safely-by-a-cu.patch
ApplyPatch 0115-livepatch-Allow-to-call-a-custom-callback-when-freei.patch
ApplyPatch 0116-livepatch-Remove-reliable-stacktrace-check-in-klp_tr.patch
ApplyPatch 0117-livepatch-Replace-synchronize_sched-with-synchronize.patch
ApplyPatch 0118-livepatch-Change-unsigned-long-old_addr-void-old_fun.patch
ApplyPatch 0119-xen-Restore-xen-pirqs-on-resume-from-hibernation.patch
ApplyPatch 0120-block-add-io-timeout-to-sysfs.patch
ApplyPatch 0121-block-don-t-show-io_timeout-if-driver-has-no-timeout.patch
ApplyPatch 0122-Add-Amazon-EFA-driver-version-1.4.patch
ApplyPatch 0123-percpu-refcount-Introduce-percpu_ref_resurrect.patch
ApplyPatch 0124-block-Allow-unfreezing-of-a-queue-while-requests-are.patch
ApplyPatch 0125-nvme-change-namespaces_mutext-to-namespaces_rwsem.patch
ApplyPatch 0126-blk-mq-fix-hang-caused-by-freeze-unfreeze-sequence.patch
ApplyPatch 0127-nvme-move-the-dying-queue-check-from-cancel-to-compl.patch
ApplyPatch 0128-nvme-pci-Better-support-for-disabling-controller.patch
ApplyPatch 0129-nvme-host-core-Allow-overriding-of-wait_ready-timeou.patch
ApplyPatch 0130-nvme-host-pci-Fix-a-race-in-controller-removal.patch
ApplyPatch 0131-nvme-pci-move-cq_vector-1-check-outside-of-q_lock.patch
ApplyPatch 0132-irqchip-gic-v3-its-Pass-its_node-pointer-to-each-com.patch
ApplyPatch 0133-irqchip-gic-v3-its-Only-emit-SYNC-if-targetting-a-va.patch
ApplyPatch 0134-irqchip-gic-v3-its-Only-emit-VSYNC-if-targetting-a-v.patch
ApplyPatch 0135-irqchip-gic-v3-its-Refactor-LPI-allocator.patch
ApplyPatch 0136-irqchip-gic-v3-its-Use-full-range-of-LPIs.patch
ApplyPatch 0137-irqchip-gic-v3-its-Move-minimum-LPI-requirements-to-.patch
ApplyPatch 0138-irqchip-gic-v3-its-Drop-chunk-allocation-compatibili.patch
ApplyPatch 0139-irqchip-gic-v3-Expose-GICD_TYPER-in-the-rdist-struct.patch
ApplyPatch 0140-irqchip-gic-v3-its-Honor-hypervisor-enforced-LPI-ran.patch
ApplyPatch 0141-irqchip-gic-v3-its-Reduce-minimum-LPI-allocation-to-.patch
ApplyPatch 0142-irqchip-gic-v3-its-Cap-lpi_id_bits-to-reduce-memory-.patch
ApplyPatch 0143-irqchip-gic-v3-its-Gracefully-fail-on-LPI-exhaustion.patch
ApplyPatch 0144-irqchip-gic-v3-its-Fix-comparison-logic-in-lpi_range.patch
ApplyPatch 0145-iommu-io-pgtable-arm-Convert-to-IOMMU-API-TLB-sync.patch
ApplyPatch 0146-iommu-io-pgtable-arm-v7s-Convert-to-IOMMU-API-TLB-sy.patch
ApplyPatch 0147-iommu-arm-smmu-v3-Implement-flush_iotlb_all-hook.patch
ApplyPatch 0148-iommu-dma-Add-support-for-non-strict-mode.patch
ApplyPatch 0149-iommu-Add-iommu.strict-command-line-option.patch
ApplyPatch 0150-iommu-io-pgtable-arm-Add-support-for-non-strict-mode.patch
ApplyPatch 0151-iommu-arm-smmu-v3-Add-support-for-non-strict-mode.patch
ApplyPatch 0152-iommu-io-pgtable-arm-v7s-Add-support-for-non-strict-.patch
ApplyPatch 0153-iommu-arm-smmu-Support-non-strict-mode.patch
ApplyPatch 0154-iommu-use-config-option-to-specify-if-iommu-mode-sho.patch
ApplyPatch 0155-locking-atomic-Add-atomic_cond_read_acquire.patch
ApplyPatch 0156-locking-barriers-Introduce-smp_cond_load_relaxed-and.patch
ApplyPatch 0157-locking-qspinlock-Use-atomic_cond_read_acquire.patch
ApplyPatch 0158-locking-mcs-Use-smp_cond_load_acquire-in-MCS-spin-lo.patch
ApplyPatch 0159-locking-qspinlock-Use-smp_cond_load_relaxed-to-wait-.patch
ApplyPatch 0160-locking-qspinlock-Use-smp_store_release-in-queued_sp.patch
ApplyPatch 0161-locking-qspinlock-Elide-back-to-back-RELEASE-operati.patch
ApplyPatch 0162-locking-qspinlock-Use-try_cmpxchg-instead-of-cmpxchg.patch
ApplyPatch 0163-MAINTAINERS-Add-myself-as-a-co-maintainer-for-the-lo.patch
ApplyPatch 0164-arm64-barrier-Implement-smp_cond_load_relaxed.patch
ApplyPatch 0165-arm64-locking-Replace-ticket-lock-implementation-wit.patch
ApplyPatch 0166-arm64-kconfig-Ensure-spinlock-fastpaths-are-inlined-.patch
ApplyPatch 0167-arm64-pull-in-upstream-erratum-workarounds.patch
ApplyPatch 0168-arm64-Avoid-flush_icache_range-in-alternatives-patch.patch
ApplyPatch 0169-update-ena-driver-to-version-2.1.3.patch
ApplyPatch 0170-Revert-nvme-pci-Better-support-for-disabling-control.patch
ApplyPatch 0171-nvme-pci-introduce-RECONNECTING-state-to-mark-initia.patch
ApplyPatch 0172-nvme-allow-controller-RESETTING-to-RECONNECTING-tran.patch
ApplyPatch 0173-nvme-rename-NVME_CTRL_RECONNECTING-state-to-NVME_CTR.patch
ApplyPatch 0174-nvme-pci-Fix-timeouts-in-connecting-state.patch
ApplyPatch 0175-nvme-pci-shutdown-on-timeout-during-deletion.patch
ApplyPatch 0176-nvme-pci-Unblock-reset_work-on-IO-failure.patch
ApplyPatch 0177-nvme-pci-Don-t-disable-on-timeout-in-reset-state.patch
ApplyPatch 0178-nvme-pci-use-atomic-bitops-to-mark-a-queue-enabled.patch
ApplyPatch 0179-arm64-fix-merge-error-in-errata-changes.patch
ApplyPatch 0180-lustre-hold-lock-while-walking-changelog-dev-list.patch
ApplyPatch 0181-Revert-Fix-the-locking-in-dcache_readdir-and-friends.patch
ApplyPatch 0182-drivers-amazon-efa-update-to-1.5.0.patch
ApplyPatch 0183-SMB3-Backup-intent-flag-missing-from-compounded-ops.patch
ApplyPatch 0184-Add-support-for-setting-owner-info-dos-attributes-an.patch

# Any further pre-build tree manipulations happen here.

chmod +x scripts/checkpatch.pl

touch .scmversion

# only deal with configs if we are going to build for the arch
%ifnarch %nobuildarches

mkdir configs

# Remove configs not for the buildarch
for cfg in kernel-%{version}-*.config; do
  if [ `echo %{all_arch_configs} | grep -c $cfg` -eq 0 ]; then
    rm -f $cfg
  fi
done

%if !%{debugbuildsenabled}
rm -f kernel-%{version}-*debug.config
%endif

# now run oldconfig over all the config files
for i in *.config
do
  mv $i .config
  Arch=`head -1 .config | cut -b 3-`
%if %{with_oldconfig}
  make ARCH=$Arch %{oldconfig_target}
%endif
  echo "# $Arch" > configs/$i
  cat .config >> configs/$i
done
# end of kernel config
%endif

# get rid of unwanted files resulting from patch fuzz
find . \( -name "*.orig" -o -name "*~" \) -exec rm -f {} \; >/dev/null

cd ..

###
### build
###
%build

%if %{with_sparse}
%define sparse_mflags	C=1
%endif

%if %{with_debuginfo}
# This override tweaks the kernel makefiles so that we run debugedit on an
# object before embedding it.  When we later run find-debuginfo.sh, it will
# run debugedit again.  The edits it does change the build ID bits embedded
# in the stripped object, but repeating debugedit is a no-op.  We do it
# beforehand to get the proper final build ID bits into the embedded image.
# This affects the vDSO images in vmlinux, and the vmlinux image in bzImage.
export AFTER_LINK=\
'sh -xc "/usr/lib/rpm/debugedit -b $$RPM_BUILD_DIR -d /usr/src/debug \
    				-i $@ > $@.id"'
%endif

cp_vmlinux()
{
  eu-strip --remove-comment -o "$2" "$1"
}

export CC=%{?_gcc}%{?!_gcc:gcc}
export HOSTCC=%{?_gcc}%{?!_gcc:gcc}
export HOSTCXX=%{?_gxx}%{?!_gxx:g++}

%global make_defines CC=gcc HOSTCC=gcc HOSTCXX=g++

export KBUILD_BUILD_HOST=$(hostname --short)

BuildKernel() {
    MakeTarget=$1
    KernelImage=$2
    Flavour=$3
    Flav=${Flavour:+.${Flavour}}
    InstallName=${4:-vmlinuz}

    # Pick the right config file for the kernel we're building
    Config=kernel-%{version}-%{_target_cpu}${Flavour:+-${Flavour}}.config
    DevelDir=/usr/src/kernels/%{KVERREL}${Flav}

    # When the bootable image is just the ELF kernel, strip it.
    # We already copy the unstripped file into the debuginfo package.
    if [ "$KernelImage" = vmlinux ]; then
      CopyKernel=cp_vmlinux
    else
      CopyKernel=cp
    fi

    KernelVer=%{version}-%{release}.%{_target_cpu}${Flav}
    echo BUILDING A KERNEL FOR ${Flavour} %{_target_cpu}...

    # make sure EXTRAVERSION says what we want it to say
    perl -p -i -e "s/^EXTRAVERSION.*/EXTRAVERSION = -%{release}.%{_target_cpu}${Flav}/" Makefile

    # and now to start the build process

    make -s mrproper
    cp configs/$Config .config

%if %{signmodules}
    cp %{SOURCE11} .
    chmod +x scripts/sign-file
%endif

    Arch=`head -1 .config | cut -b 3-`
    echo USING ARCH=$Arch

    make -s ARCH=$Arch %{oldconfig_target} %{?make_defines} > /dev/null
    make -s ARCH=$Arch V=1 %{?_smp_mflags} $MakeTarget %{?sparse_mflags} %{?make_defines}
    make -s ARCH=$Arch V=1 %{?_smp_mflags} modules %{?sparse_mflags} %{?make_defines} || exit 1

    # Start installing the results
%if %{with_debuginfo}
    mkdir -p $RPM_BUILD_ROOT%{debuginfodir}/boot
    mkdir -p $RPM_BUILD_ROOT%{debuginfodir}/%{image_install_path}
%endif
    mkdir -p $RPM_BUILD_ROOT/%{image_install_path}
    install -m 644 .config $RPM_BUILD_ROOT/boot/config-$KernelVer
    install -m 644 System.map $RPM_BUILD_ROOT/boot/System.map-$KernelVer

%if %{with_dracut}
    # We estimate the size of the initramfs because rpm needs to take this size
    # into consideration when performing disk space calculations. (See bz #530778)
    dd if=/dev/zero of=$RPM_BUILD_ROOT/boot/initramfs-$KernelVer.img bs=1M count=20
%else
    dd if=/dev/zero of=$RPM_BUILD_ROOT/boot/initrd-$KernelVer.img bs=1M count=5
%endif

    if [ -f arch/$Arch/boot/zImage.stub ]; then
      cp arch/$Arch/boot/zImage.stub $RPM_BUILD_ROOT/%{image_install_path}/zImage.stub-$KernelVer || :
    fi
    %if %{signmodules}
    # Sign the image if we're using EFI
    %pesign -s -i $KernelImage -o vmlinuz.signed
    if [ ! -s vmlinuz.signed ]; then
        echo "pesigning failed"
        exit 1
    fi
    mv vmlinuz.signed $KernelImage
    %endif
    $CopyKernel $KernelImage \
    		$RPM_BUILD_ROOT/%{image_install_path}/$InstallName-$KernelVer
    chmod 755 $RPM_BUILD_ROOT/%{image_install_path}/$InstallName-$KernelVer

    mkdir -p $RPM_BUILD_ROOT/lib/modules/$KernelVer
    # Override $(mod-fw) because we don't want it to install any firmware
    # we'll get it from the linux-firmware package and we don't want conflicts
    make -s ARCH=$Arch INSTALL_MOD_PATH=$RPM_BUILD_ROOT modules_install KERNELRELEASE=$KernelVer mod-fw=

%ifarch %{vdso_arches}
    make -s ARCH=$Arch INSTALL_MOD_PATH=$RPM_BUILD_ROOT vdso_install KERNELRELEASE=$KernelVer
    if grep '^CONFIG_XEN=y$' .config >/dev/null ; then
        echo > ldconfig-kernel.conf "\
# This directive teaches ldconfig to search in nosegneg subdirectories
# and cache the DSOs there with extra bit 0 set in their hwcap match
# fields.  In Xen guest kernels, the vDSO tells the dynamic linker to
# search in nosegneg subdirectories and to match this extra hwcap bit
# in the ld.so.cache file.
hwcap 1 nosegneg"
    fi
    if [ ! -s ldconfig-kernel.conf ]; then
      echo > ldconfig-kernel.conf "\
# Placeholder file, no vDSO hwcap entries used in this kernel."
    fi
    %{__install} -D -m 444 ldconfig-kernel.conf \
        $RPM_BUILD_ROOT/etc/ld.so.conf.d/kernel-$KernelVer.conf
%endif

    # And save the headers/makefiles etc for building modules against
    #
    # This all looks scary, but the end result is supposed to be:
    # * all arch relevant include/ files
    # * all Makefile/Kconfig files
    # * all script/ files

    rm -f $RPM_BUILD_ROOT/lib/modules/$KernelVer/build
    rm -f $RPM_BUILD_ROOT/lib/modules/$KernelVer/source
    mkdir -p $RPM_BUILD_ROOT/lib/modules/$KernelVer/build
    (cd $RPM_BUILD_ROOT/lib/modules/$KernelVer ; ln -s build source)
    # dirs for additional modules per module-init-tools, kbuild/modules.txt
    mkdir -p $RPM_BUILD_ROOT/lib/modules/$KernelVer/extra
    mkdir -p $RPM_BUILD_ROOT/lib/modules/$KernelVer/updates
    mkdir -p $RPM_BUILD_ROOT/lib/modules/$KernelVer/weak-updates
    # first copy everything
    cp --parents `find  -type f -name "Makefile*" -o -name "Kconfig*"` $RPM_BUILD_ROOT/lib/modules/$KernelVer/build
    cp Module.symvers $RPM_BUILD_ROOT/lib/modules/$KernelVer/build
    gzip -c9 Module.symvers >  $RPM_BUILD_ROOT/boot/symvers-$KernelVer.gz
    cp System.map $RPM_BUILD_ROOT/lib/modules/$KernelVer/build
    if [ -s Module.markers ]; then
      cp Module.markers $RPM_BUILD_ROOT/lib/modules/$KernelVer/build
    fi
    # then drop all but the needed Makefiles/Kconfig files
    rm -rf $RPM_BUILD_ROOT/lib/modules/$KernelVer/build/Documentation
    rm -rf $RPM_BUILD_ROOT/lib/modules/$KernelVer/build/scripts
    rm -rf $RPM_BUILD_ROOT/lib/modules/$KernelVer/build/include
    cp .config $RPM_BUILD_ROOT/lib/modules/$KernelVer/build
    if [ -f tools/objtool/objtool ]; then
      cp -a tools/objtool/objtool $RPM_BUILD_ROOT/lib/modules/$KernelVer/build/tools/objtool/ || :
    fi
    cp -a scripts $RPM_BUILD_ROOT/lib/modules/$KernelVer/build
    if [ -d arch/$Arch/scripts ]; then
      cp -a arch/$Arch/scripts $RPM_BUILD_ROOT/lib/modules/$KernelVer/build/arch/%{_arch} || :
    fi
    if [ -f arch/$Arch/*lds ]; then
      cp -a arch/$Arch/*lds $RPM_BUILD_ROOT/lib/modules/$KernelVer/build/arch/%{_arch}/ || :
    fi
    rm -f $RPM_BUILD_ROOT/lib/modules/$KernelVer/build/scripts/*.o
    rm -f $RPM_BUILD_ROOT/lib/modules/$KernelVer/build/scripts/*/*.o
    if [ -d arch/%{asmarch}/include ]; then
      cp -a --parents arch/%{asmarch}/include $RPM_BUILD_ROOT/lib/modules/$KernelVer/build/
    fi
    cp -a include $RPM_BUILD_ROOT/lib/modules/$KernelVer/build/include

    # newer kernels relocate these from under include/linux to
    # include/generated.... Maintain compatibility with old(er) code looking
    # for former files in the formerly valid location
    pushd  $RPM_BUILD_ROOT/lib/modules/$KernelVer/build/include/linux
    test -s utsrelease.h        || ln -sf ../generated/utsrelease.h .
    test -s autoconf.h          || ln -sf ../generated/autoconf.h .
    test -s version.h           || ln -sf ../generated/uapi/linux/version.h .
    popd
    # Make sure the Makefile and version.h have a matching timestamp so that
    # external modules can be built
    touch -r $RPM_BUILD_ROOT/lib/modules/$KernelVer/build/Makefile $RPM_BUILD_ROOT/lib/modules/$KernelVer/build/include/linux/version.h
    touch -r $RPM_BUILD_ROOT/lib/modules/$KernelVer/build/.config $RPM_BUILD_ROOT/lib/modules/$KernelVer/build/include/linux/autoconf.h
    # Copy .config to include/config/auto.conf so "make prepare" is unnecessary.
    cp -a $RPM_BUILD_ROOT/lib/modules/$KernelVer/build/.config $RPM_BUILD_ROOT/lib/modules/$KernelVer/build/include/config/auto.conf

%if %{with_debuginfo}
%if %{fancy_debuginfo}
    if test -s vmlinux.id; then
      cp vmlinux.id $RPM_BUILD_ROOT/lib/modules/$KernelVer/build/vmlinux.id
    else
      echo >&2 "*** ERROR *** no vmlinux build ID! ***"
      exit 1
    fi
%endif # fancy_debuginfo
    #
    # save the vmlinux file for kernel debugging into the kernel-debuginfo rpm
    #
    mkdir -p $RPM_BUILD_ROOT%{debuginfodir}/lib/modules/$KernelVer
    cp vmlinux $RPM_BUILD_ROOT%{debuginfodir}/lib/modules/$KernelVer
%endif #debuginfo

    find $RPM_BUILD_ROOT/lib/modules/$KernelVer -name "*.ko" -type f >modnames

    # mark modules executable so that strip-to-file can strip them
    xargs --no-run-if-empty chmod u+x < modnames

    # Generate a list of modules for block and networking.

    grep -F /drivers/ modnames | xargs --no-run-if-empty nm -upA |
    sed -n 's,^.*/\([^/]*\.ko\):  *U \(.*\)$,\1 \2,p' > drivers.undef

    collect_modules_list()
    {
      sed -r -n -e "s/^([^ ]+) \\.?($2)\$/\\1/p" drivers.undef |
      LC_ALL=C sort -u > $RPM_BUILD_ROOT/lib/modules/$KernelVer/modules.$1
    }

    collect_modules_list networking \
                        'register_netdev|ieee80211_register_hw|usbnet_probe|phy_driver_register|rt(l_|2x00)(pci|usb)_probe|register_netdevice'
    collect_modules_list block \
                        'ata_scsi_ioctl|scsi_add_host|scsi_add_host_with_dma|blk_init_queue|register_mtd_blktrans|scsi_esp_register|scsi_register_device_handler|blk_queue_physical_block_size'
    collect_modules_list drm \
                        'drm_open|drm_init'
    collect_modules_list modesetting \
                        'drm_crtc_init'

    # detect missing or incorrect license tags
    rm -f modinfo
    while read i
    do
      echo -n "${i#$RPM_BUILD_ROOT/lib/modules/$KernelVer/} " >> modinfo
      %{_sbindir}/modinfo -l $i >> modinfo
    done < modnames

    grep -E -v \
    	  'GPL( v2)?$|Dual BSD/GPL$|Dual MPL/GPL$|GPL and additional rights$' \
	  modinfo && exit 1

    rm -f modinfo modnames

    # Call the modules-extra script to move things around
    %{SOURCE17} $RPM_BUILD_ROOT/lib/modules/$KernelVer %{SOURCE16}

%if %{signmodules}
    # Save off the .tmp_versions/ directory.  We'll use it in the
    # __debug_install_post macro below to sign the right things
    # Also save the signing keys so we actually sign the modules with the
    # right key.
    cp -r .tmp_versions .tmp_versions.sign${Flavour:+.${Flavour}}
    cp signing_key.priv signing_key.priv.sign${Flavour:+.${Flavour}}
    cp signing_key.x509 signing_key.x509.sign${Flavour:+.${Flavour}}
%endif

    # remove files that will be auto generated by depmod at rpm -i time
    for i in alias alias.bin builtin.bin ccwmap dep dep.bin ieee1394map inputmap isapnpmap ofmap pcimap seriomap symbols symbols.bin usbmap devname softdep
    do
      rm -f $RPM_BUILD_ROOT/lib/modules/$KernelVer/modules.$i
    done

    # Move the devel headers out of the root file system
    mkdir -p $RPM_BUILD_ROOT/usr/src/kernels
    mv $RPM_BUILD_ROOT/lib/modules/$KernelVer/build $RPM_BUILD_ROOT/$DevelDir
    ln -sf ../../..$DevelDir $RPM_BUILD_ROOT/lib/modules/$KernelVer/build

    # prune junk from kernel-devel
    find $RPM_BUILD_ROOT/usr/src/kernels -name ".*.cmd" -exec rm -f {} \;
}

###
# DO it...
###

# prepare directories
rm -rf $RPM_BUILD_ROOT
mkdir -p $RPM_BUILD_ROOT/boot
mkdir -p $RPM_BUILD_ROOT%{_libexecdir}

cd linux-%{KVERREL}

%if %{with_debug}
BuildKernel %make_target %kernel_image debug
%endif

%if %{with_up}
BuildKernel %make_target %kernel_image
%endif

# perf
%if 0%{?_sys_python:1}
  perfPYTHON=%{_sys_python}
%else
  perfPYTHON=%{_python}
%endif
%global perf_make \
  make %{?_smp_mflags} -C tools/perf -s V=1 EXTRA_CFLAGS="-Wno-error=array-bounds" \\\
  HAVE_CPLUS_DEMANGLE=1 NO_LIBUNWIND=1 NO_GTK2=1 NO_STRLCPY=1 \\\
  prefix=%{_prefix} \\\
  PYTHON=$perfPYTHON \\\
  PYTHON_INSTALL_LAYOUT="amzn"

%if %{with_perf}
%{perf_make} all
%{perf_make} man || %{doc_build_fail}
%endif

%if %{with_tools}
%ifarch %{cpupowerarchs}
# cpupower
# make sure version-gen.sh is executable.
chmod +x tools/power/cpupower/utils/version-gen.sh
make %{?_smp_mflags} -C tools/power/cpupower CPUFREQ_BENCH=false
%ifarch %{ix86}
    pushd tools/power/cpupower/debug/i386
    make %{?_smp_mflags} centrino-decode powernow-k8-decode
    popd
%endif # ix86
%ifarch x86_64
    pushd tools/power/cpupower/debug/x86_64
    make %{?_smp_mflags} centrino-decode powernow-k8-decode
    popd
%endif # x86_64
%ifarch %{ix86} x86_64
   pushd tools/power/x86/x86_energy_perf_policy/
   make
   popd
   pushd tools/power/x86/turbostat
   make
   popd
%endif #turbostat/x86_energy_perf_policy
%endif # cpupowerarchs
%endif # tools

%if %{with_doc}
#
# Make the HTML documents.
# Newer kernel versions use ReST markups for documentation which
# needs to be built using Sphinx. Sphinx toolchain is fragile and any
# upgrade to its toolchain or dependent python package can cause
# documentation build to fail. To avoid this problem, documentation
# build uses one particular version of Sphinx. To build document,
# we create a virtual environment and install the required version
# of Sphinx inside it.
# Refer to $SRC/Documentation/sphinx/requirements.txt for more
# information related to package and version dependency.
#
virtualenv doc_build_env
source ./doc_build_env/bin/activate
pip install -r Documentation/sphinx/requirements.txt
make htmldocs || %{doc_build_fail}
deactivate
rm -rf doc_build_env

# Build man pages for the kernel API (section 9)
scripts/kernel-doc -man $(find . -name '*.[ch]') | %{split_man_cmd} Documentation/output/man
pushd Documentation/output/man
gzip *.9
popd

# sometimes non-world-readable files sneak into the kernel source tree
chmod -R a=rX Documentation
find Documentation -type d | xargs chmod u+w

# switch absolute symlinks to relative ones
find . -lname "$(pwd)*" -exec sh -c 'ln -snvf $(python -c "from os.path import *; print relpath(\"$(readlink {})\",dirname(\"{}\"))") {}' \;
%endif # with_doc

# In the modsign case, we do 3 things.  1) We check the "flavour" and hard
# code the value in the following invocations.  This is somewhat sub-optimal
# but we're doing this inside of an RPM macro and it isn't as easy as it
# could be because of that.  2) We restore the .tmp_versions/ directory from
# the one we saved off in BuildKernel above.  This is to make sure we're
# signing the modules we actually built/installed in that flavour.  3) We
# grab the arch and invoke mod-sign.sh command to actually sign the modules.
#
# We have to do all of those things _after_ find-debuginfo runs, otherwise
# that will strip the signature off of the modules.
%define __modsign_install_post \
  if [ "%{signmodules}" == "1" ]; then \
    if [ "%{with_debug}" != "0" ]; \
    then \
      Arch=`head -1 configs/kernel-%{version}-%{_target_cpu}-debug.config | cut -b 3-` \
      rm -rf .tmp_versions \
      mv .tmp_versions.sign.debug .tmp_versions \
      mv signing_key.priv.sign.debug signing_key.priv \
      mv signing_key.x509.sign.debug signing_key.x509 \
      make -s ARCH=$Arch V=1 INSTALL_MOD_PATH=$RPM_BUILD_ROOT modules_sign KERNELRELEASE=%{KVERREL}.debug \
      %{modsign_cmd} $RPM_BUILD_ROOT/lib/modules/%{KVERREL}.debug/extra/ \
    fi \
  fi \
%{nil}

###
### Special hacks for debuginfo subpackages.
###

# This macro is used by %%install, so we must redefine it before that.
%define debug_package %{nil}

%if %{with_debuginfo}
%if %{fancy_debuginfo}
%define __debug_install_post \
  /usr/lib/rpm/find-debuginfo.sh %{debuginfo_args} %{_builddir}/%{?buildsubdir}\
%{nil}
%endif # fancy_debuginfo

%ifnarch noarch
%global __debug_package 1
%files -f debugfiles.list debuginfo-common-%{_target_cpu}
%defattr(-,root,root)
%endif # noarch

%endif # debuginfo

#
# Disgusting hack alert! We need to ensure we sign modules *after* all
# invocations of strip occur, which is in __debug_install_post if
# find-debuginfo.sh runs, and __os_install_post if not.
%define __spec_install_post \
  %{?__debug_package:%{__debug_install_post}}\
  %{__arch_install_post}\
  %{__os_install_post}\
  %{__modsign_install_post}

###
### install
###

%install

cd linux-%{KVERREL}

%if %{with_doc}
docdir=$RPM_BUILD_ROOT%{_datadir}/doc/kernel-doc-%{rpmversion}
man9dir=$RPM_BUILD_ROOT%{_datadir}/man/man9

# copy the source over
mkdir -p $docdir
tar -f - --exclude=man --exclude='.*' -c Documentation | tar xf - -C $docdir

# Install man pages for the kernel API.
mkdir -p $man9dir
pushd Documentation/output/man
find -type f -name '*.9.gz' -print0 |
xargs -0 --no-run-if-empty %{__install} -m 444 -t $man9dir $m
popd
ls $man9dir | grep -q '' || > $man9dir/BROKEN
%endif # with_doc

# We have to do the headers install before the tools install because the
# kernel headers_install will remove any header files in /usr/include that
# it doesn't install itself.

%if %{with_headers}
# Install kernel headers
make -s ARCH=%{hdrarch} INSTALL_HDR_PATH=$RPM_BUILD_ROOT/usr headers_install

# Do headers_check but don't die if it fails.
make -s ARCH=%{hdrarch} INSTALL_HDR_PATH=$RPM_BUILD_ROOT/usr headers_check \
     > hdrwarnings.txt || :
if grep -q exist hdrwarnings.txt; then
   sed s:^$RPM_BUILD_ROOT/usr/include/:: hdrwarnings.txt
   # Temporarily cause a build failure if header inconsistencies.
   # exit 1
fi

find $RPM_BUILD_ROOT/usr/include \
     \( -name .install -o -name .check -o \
     	-name ..install.cmd -o -name ..check.cmd \) | xargs rm -f

# glibc provides scsi headers for itself, for now
rm -rf $RPM_BUILD_ROOT/usr/include/scsi
rm -f $RPM_BUILD_ROOT/usr/include/asm*/atomic.h
rm -f $RPM_BUILD_ROOT/usr/include/asm*/io.h
rm -f $RPM_BUILD_ROOT/usr/include/asm*/irq.h
%endif

%if %{with_perf}
# perf tool binary and supporting scripts/binaries
%{perf_make} DESTDIR=$RPM_BUILD_ROOT install
# python-perf extension
%{perf_make} DESTDIR=$RPM_BUILD_ROOT install-python_ext
# perf man pages (note: implicit rpm magic compresses them later)
%{perf_make} DESTDIR=$RPM_BUILD_ROOT install-man || %{doc_build_fail}
# clean up files we don't use
rm -f $RPM_BUILD_ROOT/etc/bash_completion.d/perf
%endif

%if %{with_tools}
%ifarch %{cpupowerarchs}
make -C tools/power/cpupower DESTDIR=$RPM_BUILD_ROOT libdir=%{_libdir} mandir=%{_mandir} CPUFREQ_BENCH=false install
rm -f %{buildroot}%{_libdir}/*.{a,la}
%find_lang cpupower
mv cpupower.lang ../
%ifarch %{ix86}
    pushd tools/power/cpupower/debug/i386
    install -m755 centrino-decode %{buildroot}%{_bindir}/centrino-decode
    install -m755 powernow-k8-decode %{buildroot}%{_bindir}/powernow-k8-decode
    popd
%endif
%ifarch x86_64
    pushd tools/power/cpupower/debug/x86_64
    install -m755 centrino-decode %{buildroot}%{_bindir}/centrino-decode
    install -m755 powernow-k8-decode %{buildroot}%{_bindir}/powernow-k8-decode
    popd
%endif
%ifarch %{ix86} x86_64
   mkdir -p %{buildroot}%{_mandir}/man8
   pushd tools/power/x86/x86_energy_perf_policy
   make DESTDIR=%{buildroot} install
   popd
   pushd tools/power/x86/turbostat
   make DESTDIR=%{buildroot} install
   popd
%endif #turbostat/x86_energy_perf_policy
chmod 0755 %{buildroot}%{_libdir}/libcpupower.so*
mkdir -p %{buildroot}%{_initddir} %{buildroot}%{_sysconfdir}/sysconfig
#install -m644 %{SOURCE2000} %{buildroot}%{_initddir}/cpupower
install -m644 %{SOURCE2001} %{buildroot}%{_sysconfdir}/sysconfig/cpupower
%endif # cpupowerarchs
# just in case so the files list won't croak
touch ../cpupower.lang
%endif # tools


###
### clean
###

%clean
rm -rf $RPM_BUILD_ROOT

###
### scripts
###

%if %{with_tools}
%post tools
/sbin/ldconfig

%postun tools
/sbin/ldconfig
%endif

#
# This macro defines a %%post script for a kernel*-devel package.
#	%%kernel_devel_post [<subpackage>]
#
%define kernel_devel_post() \
%{expand:%%post %{?1:%{1}-}devel}\
if [ -f /etc/sysconfig/kernel ]\
then\
    . /etc/sysconfig/kernel || exit $?\
fi\
if [ "$HARDLINK" != "no" -a -x /usr/sbin/hardlink ]\
then\
    (cd /usr/src/kernels/%{KVERREL}%{?1:.%{1}} &&\
     /usr/bin/find . -type f | while read f; do\
       hardlink -c /usr/src/kernels/*.%{dist}.*/$f $f\
     done)\
fi\
%{nil}

# This macro defines a %%posttrans script for a kernel package.
#	%%kernel_variant_posttrans [<subpackage>]
# More text can follow to go at the end of this variant's %%post.
#
%define kernel_variant_posttrans() \
%{expand:%%posttrans %{?1}}\
%{expand:\
%if %{with_dracut}\
/sbin/new-kernel-pkg --package kernel%{?1:-%{1}} --mkinitrd --make-default --dracut --depmod --install %{KVERREL}%{?1:-%{1}} || exit $?\
%else\
/sbin/new-kernel-pkg --package kernel%{?1:-%{1}} --mkinitrd --make-default --depmod --install %{KVERREL}%{?1:-%{1}} || exit $?\
%endif\
}\
/sbin/new-kernel-pkg --package kernel%{?1:-%{1}} --rpmposttrans %{KVERREL}%{?1:.%{1}} || exit $?\
%{nil}

#
# This macro defines a %%post script for a kernel package and its devel package.
#	%%kernel_variant_post [-v <subpackage>] [-r <replace>]
# More text can follow to go at the end of this variant's %%post.
#
%define kernel_variant_post(v:r:) \
%{expand:%%kernel_devel_post %{?-v*}}\
%{expand:%%kernel_variant_posttrans %{?-v*}}\
%{expand:%%post %{?-v*}}\
%{-r:\
if [ `uname -i` == "x86_64" -o `uname -i` == "i386" ] &&\
   [ -f /etc/sysconfig/kernel ]; then\
  /bin/sed -r -i -e 's/^DEFAULTKERNEL=%{-r*}$/DEFAULTKERNEL=kernel%{?-v:-%{-v*}}/' /etc/sysconfig/kernel || exit $?\
fi}\
%{nil}

#
# This macro defines a %%preun script for a kernel package.
#	%%kernel_variant_preun <subpackage>
#
%define kernel_variant_preun() \
%{expand:%%preun %{?1}}\
/sbin/new-kernel-pkg --rminitrd --rmmoddep --remove %{KVERREL}%{?1:.%{1}} || exit $?\
%{nil}

%kernel_variant_preun
%kernel_variant_post

%kernel_variant_preun debug
%kernel_variant_post -v debug

if [ -x /sbin/ldconfig ]
then
    /sbin/ldconfig -X || exit $?
fi

###
### file lists
###

%if %{with_headers}
%files headers
%defattr(-,root,root)
/usr/include/*
%endif

# only some architecture builds need kernel-doc
%if %{with_doc}
%files doc
%defattr(-,root,root)
%{_datadir}/doc/kernel-doc-%{rpmversion}/Documentation/*
%dir %{_datadir}/doc/kernel-doc-%{rpmversion}/Documentation
%dir %{_datadir}/doc/kernel-doc-%{rpmversion}
%{_datadir}/man/man9/*
%endif

%if %{with_perf}
%files -n perf
%defattr(-,root,root)
%{_bindir}/perf
%{_bindir}/trace
%dir %{_libexecdir}/perf-core
%{_libexecdir}/perf-core/*
%{_datadir}/perf-core/*
%{_datadir}/doc/perf*/*
%dir %{_libdir}/traceevent/plugins
%{_libdir}/traceevent/plugins/*
%{_mandir}/man[1-8]/perf*
%doc linux-%{KVERREL}/tools/perf/Documentation/examples.txt
%if 0%{?_sys_python_sitearch:1}
%{_sys_python_sitearch}/*
%else
%{_python_sitearch}/*
%endif

%if %{with_debuginfo}
%files -f perf-debuginfo.list -n perf-debuginfo
%defattr(-,root,root)
%endif
%endif # with_perf

%if %{with_tools}
%files tools -f cpupower.lang
%defattr(-,root,root)
%{_mandir}/man[1-8]/cpupower*
%{_bindir}/cpupower
%ifarch %{ix86} x86_64
%{_bindir}/centrino-decode
%{_bindir}/powernow-k8-decode
%{_bindir}/x86_energy_perf_policy
%{_mandir}/man8/x86_energy_perf_policy*
%{_bindir}/turbostat
%{_mandir}/man8/turbostat*
%endif
%{_libdir}/libcpupower.so.0
%{_libdir}/libcpupower.so.0.0.1
#%{_initddir}/cpupower
%config(noreplace) %{_sysconfdir}/sysconfig/cpupower

%if %{with_debuginfo}
%files tools-debuginfo -f kernel-tools-debuginfo.list
%defattr(-,root,root)
%endif

%ifarch %{cpupowerarchs}
%files tools-devel
%{_libdir}/libcpupower.so
%{_includedir}/cpufreq.h
%endif
%endif # with_tools

# This is %%{image_install_path} on an arch where that includes ELF files,
# or empty otherwise.
%define elf_image_install_path %{?kernel_image_elf:%{image_install_path}}

#
# This macro defines the %%files sections for a kernel package
# and its devel and debuginfo packages.
#	%%kernel_variant_files [-k vmlinux] <condition> <subpackage>
#
%define kernel_variant_files(k:) \
%if %{1}\
%{expand:%%files %{?2}}\
%defattr(-,root,root)\
/%{image_install_path}/%{?-k:%{-k*}}%{!?-k:vmlinuz}-%{KVERREL}%{?2:.%{2}}\
%attr(600,root,root) /boot/System.map-%{KVERREL}%{?2:.%{2}}\
/boot/symvers-%{KVERREL}%{?2:.%{2}}.gz\
/boot/config-%{KVERREL}%{?2:.%{2}}\
%dir /lib/modules/%{KVERREL}%{?2:.%{2}}\
/lib/modules/%{KVERREL}%{?2:.%{2}}/kernel\
/lib/modules/%{KVERREL}%{?2:.%{2}}/build\
/lib/modules/%{KVERREL}%{?2:.%{2}}/source\
/lib/modules/%{KVERREL}%{?2:.%{2}}/extra\
/lib/modules/%{KVERREL}%{?2:.%{2}}/updates\
/lib/modules/%{KVERREL}%{?2:.%{2}}/weak-updates\
%ifarch %{vdso_arches}\
/lib/modules/%{KVERREL}%{?2:.%{2}}/vdso\
/etc/ld.so.conf.d/kernel-%{KVERREL}%{?2:.%{2}}.conf\
%endif\
/lib/modules/%{KVERREL}%{?2:.%{2}}/modules.*\
%if %{with_dracut}\
%ghost /boot/initramfs-%{KVERREL}%{?2:.%{2}}.img\
%else\
%ghost /boot/initrd-%{KVERREL}%{?2:.%{2}}.img\
%endif\
%{expand:%%files %{?2:%{2}-}devel}\
%defattr(-,root,root)\
%verify(not mtime) /usr/src/kernels/%{KVERREL}%{?2:.%{2}}\
%dir /usr/src/kernels\
%if %{with_debuginfo}\
%ifnarch noarch\
%if %{fancy_debuginfo}\
%{expand:%%files -f debuginfo%{?2}.list %{?2:%{2}-}debuginfo}\
%else\
%{expand:%%files %{?2:%{2}-}debuginfo}\
%endif\
%defattr(-,root,root)\
%if !%{fancy_debuginfo}\
%if "%{elf_image_install_path}" != ""\
%{debuginfodir}/%{elf_image_install_path}/*-%{KVERREL}%{?2:.%{2}}.debug\
%endif\
%{debuginfodir}/lib/modules/%{KVERREL}%{?2:.%{2}}\
%{debuginfodir}/usr/src/kernels/%{KVERREL}%{?2:.%{2}}\
%endif\
%endif\
%endif\
%endif\
%{nil}

%kernel_variant_files %{with_up}
%kernel_variant_files %{with_debug} debug

%changelog
* Tue Dec 24 2019 Builder <builder@amazon.com>
- builder/02540f8f44d10bef4fb1d54939a4e358776f166b last changes:

- linux/b701c605edf047eda654ab00dd84675a16dcea74 last changes:
  + [b701c60] [2019-12-18] Add support for setting owner info, dos attributes, and create time (bprotopopov@hotmail.com)
  + [f796fd8] [2018-08-28] SMB3: Backup intent flag missing from compounded ops (stfrench@microsoft.com)
  + [aed9a38] [2019-12-19] drivers/amazon: efa: update to 1.5.0 (luqia@amazon.com)
  + [128b4a7] [2019-12-16] Revert "Fix the locking in dcache_readdir() and friends". (fllinden@amazon.com)
  + [c9772c4] [2019-12-04] lustre: hold lock while walking changelog dev list (astroh@amazon.com)
  + [49026e1] [2019-11-15] arm64: fix merge error in errata changes (fllinden@amazon.com)
  + [02d7944] [2019-11-12] nvme-pci: use atomic bitops to mark a queue enabled (hch@lst.de)
  + [6330404] [2019-11-11] nvme-pci: Don't disable on timeout in reset state (keith.busch@intel.com)
  + [8bbda70] [2019-11-11] nvme-pci: Unblock reset_work on IO failure (keith.busch@intel.com)
  + [a18acfe] [2019-11-11] nvme-pci: shutdown on timeout during deletion (keith.busch@intel.com)
  + [9420a3d] [2018-02-08] nvme-pci: Fix timeouts in connecting state (keith.busch@intel.com)
  + [f55a5b8] [2019-11-11] nvme: rename NVME_CTRL_RECONNECTING state to NVME_CTRL_CONNECTING (maxg@mellanox.com)
  + [114e77c] [2017-10-25] nvme: allow controller RESETTING to RECONNECTING transition (jsmart2021@gmail.com)
  + [d06cecc] [2019-11-11] nvme-pci: introduce RECONNECTING state to mark initializing procedure (jianchao.w.wang@oracle.com)
  + [cc3363e] [2019-11-11] Revert "nvme/pci: Better support for disabling controller" (sblbir@amazon.com)
  + [93c9530] [2019-11-04] update ena driver to version 2.1.3 (alakeshh@amazon.com)
  + [a281e97] [2018-06-22] arm64: Avoid flush_icache_range() in alternatives patching code (will.deacon@arm.com)
  + [2c654ec] [2018-09-27] arm64: pull in upstream erratum workarounds (fllinden@amazon.com)
  + [b6d0cc9] [2018-03-13] arm64: kconfig: Ensure spinlock fastpaths are inlined if !PREEMPT (will.deacon@arm.com)
  + [5725947] [2018-03-13] arm64: locking: Replace ticket lock implementation with qspinlock (will.deacon@arm.com)
  + [aec9adb] [2018-01-31] arm64: barrier: Implement smp_cond_load_relaxed (will.deacon@arm.com)
  + [b5ee66d] [2018-04-26] MAINTAINERS: Add myself as a co-maintainer for the locking subsystem (will.deacon@arm.com)
  + [7a1f658] [2018-04-26] locking/qspinlock: Use try_cmpxchg() instead of cmpxchg() when locking (will.deacon@arm.com)
  + [cc5b75a] [2018-04-26] locking/qspinlock: Elide back-to-back RELEASE operations with smp_wmb() (will.deacon@arm.com)
  + [b34cd4b] [2018-04-26] locking/qspinlock: Use smp_store_release() in queued_spin_unlock() (will.deacon@arm.com)
  + [ae2a618] [2018-04-26] locking/qspinlock: Use smp_cond_load_relaxed() to wait for next node (will.deacon@arm.com)
  + [ab363d8] [2018-04-26] locking/mcs: Use smp_cond_load_acquire() in MCS spin loop (jason.low2@hp.com)
  + [cbe40fa] [2018-04-26] locking/qspinlock: Use atomic_cond_read_acquire() (will.deacon@arm.com)
  + [f3dbb19] [2018-04-26] locking/barriers: Introduce smp_cond_load_relaxed() and atomic_cond_read_relaxed() (will.deacon@arm.com)
  + [6ee0e38] [2017-10-12] locking/atomic: Add atomic_cond_read_acquire() (will.deacon@arm.com)
  + [ab38f45] [2019-08-29] iommu: use config option to specify if iommu mode should be strict (fllinden@amazon.com)
  + [d44c140] [2018-09-20] iommu/arm-smmu: Support non-strict mode (robin.murphy@arm.com)
  + [8b7af36] [2018-09-20] iommu/io-pgtable-arm-v7s: Add support for non-strict mode (robin.murphy@arm.com)
  + [b913e7f] [2018-09-20] iommu/arm-smmu-v3: Add support for non-strict mode (thunder.leizhen@huawei.com)
  + [8733118] [2018-09-20] iommu/io-pgtable-arm: Add support for non-strict mode (thunder.leizhen@huawei.com)
  + [c59509e] [2018-09-20] iommu: Add "iommu.strict" command line option (thunder.leizhen@huawei.com)
  + [b29e343] [2018-09-20] iommu/dma: Add support for non-strict mode (thunder.leizhen@huawei.com)
  + [de250e9] [2018-09-20] iommu/arm-smmu-v3: Implement flush_iotlb_all hook (thunder.leizhen@huawei.com)
  + [171c4a7] [2017-09-28] iommu/io-pgtable-arm-v7s: Convert to IOMMU API TLB sync (robin.murphy@arm.com)
  + [4cb859f] [2017-09-28] iommu/io-pgtable-arm: Convert to IOMMU API TLB sync (robin.murphy@arm.com)
  + [02972b1] [2019-03-12] irqchip/gic-v3-its: Fix comparison logic in lpi_range_cmp (linux@rasmusvillemoes.dk)
  + [1c62254] [2019-01-29] irqchip/gic-v3-its: Gracefully fail on LPI exhaustion (marc.zyngier@arm.com)
  + [39504ef] [2018-08-28] irqchip/gic-v3-its: Cap lpi_id_bits to reduce memory footprint (jia.he@hxt-semitech.com)
  + [d3739d75] [2018-05-31] irqchip/gic-v3-its: Reduce minimum LPI allocation to 1 for PCI devices (marc.zyngier@arm.com)
  + [3c4b03e] [2018-05-31] irqchip/gic-v3-its: Honor hypervisor enforced LPI range (marc.zyngier@arm.com)
  + [998fee4] [2018-05-30] irqchip/gic-v3: Expose GICD_TYPER in the rdist structure (marc.zyngier@arm.com)
  + [af7f9c1] [2018-05-27] irqchip/gic-v3-its: Drop chunk allocation compatibility (marc.zyngier@arm.com)
  + [7d1b414] [2018-05-27] irqchip/gic-v3-its: Move minimum LPI requirements to individual busses (marc.zyngier@arm.com)
  + [5d673af] [2018-05-27] irqchip/gic-v3-its: Use full range of LPIs (marc.zyngier@arm.com)
  + [8bc38d4] [2018-05-27] irqchip/gic-v3-its: Refactor LPI allocator (marc.zyngier@arm.com)
  + [d5b8a96] [2018-06-22] irqchip/gic-v3-its: Only emit VSYNC if targetting a valid collection (marc.zyngier@arm.com)
  + [4c4d751] [2018-06-22] irqchip/gic-v3-its: Only emit SYNC if targetting a valid collection (marc.zyngier@arm.com)
  + [8cd472d] [2017-07-28] irqchip/gic-v3-its: Pass its_node pointer to each command builder (marc.zyngier@arm.com)
  + [02a4950] [2018-05-17] nvme-pci: move ->cq_vector == -1 check outside of ->q_lock (axboe@kernel.dk)
  + [4a681a7] [2019-09-13] nvme/host/pci: Fix a race in controller removal (sblbir@amzn.com)
  + [072d8c8] [2019-09-13] nvme/host/core: Allow overriding of wait_ready timeout (sblbir@amzn.com)
  + [8dc2b96] [2019-09-10] nvme/pci: Better support for disabling controller (sblbir@amzn.com)
  + [8aafb16] [2017-11-02] nvme: move the dying queue check from cancel to completion (hch@lst.de)
  + [d268589] [2019-08-28] blk-mq: fix hang caused by freeze/unfreeze sequence (bob.liu@oracle.com)
  + [ae26639] [2019-08-16] nvme: change namespaces_mutext to namespaces_rwsem (jianchao.w.wang@oracle.com)
  + [5d32d54] [2018-09-26] block: Allow unfreezing of a queue while requests are in progress (bvanassche@acm.org)
  + [b937931] [2019-08-16] percpu-refcount: Introduce percpu_ref_resurrect() (bvanassche@acm.org)
  + [95f86e3] [2019-09-05] Add Amazon EFA driver version 1.4 (alakeshh@amazon.com)
  + [ffa5acc] [2019-04-02] block: don't show io_timeout if driver has no timeout handler (zhangweiping@didiglobal.com)
  + [0953e77] [2018-11-29] block: add io timeout to sysfs (zhangweiping@didiglobal.com)
  + [f72c9bd] [2019-08-15] xen: Restore xen-pirqs on resume from hibernation (anchalag@amazon.com)
  + [2996ca6] [2019-01-09] livepatch: Change unsigned long old_addr -> void *old_func in struct klp_func (pmladek@suse.com)
  + [6daa0e5] [2018-11-07] livepatch: Replace synchronize_sched() with synchronize_rcu() (paulmck@linux.ibm.com)
  + [0a0edd3] [2018-07-12] livepatch: Remove reliable stacktrace check in klp_try_switch_task() (kamalesh@linux.vnet.ibm.com)
  + [b3db383] [2018-04-16] livepatch: Allow to call a custom callback when freeing shadow variables (pmladek@suse.com)
  + [00dd0e1] [2018-04-16] livepatch: Initialize shadow variables safely by a custom callback (pmladek@suse.com)
  + [1bd86c6] [2017-12-21] livepatch: add locking to force and signal functions (mbenes@suse.cz)
  + [901bfb8] [2018-01-10] livepatch: Remove immediate feature (mbenes@suse.cz)
  + [7677fef] [2017-11-22] livepatch: force transition to finish (mbenes@suse.cz)
  + [992011b] [2017-11-15] livepatch: send a fake signal to all blocking tasks (mbenes@suse.cz)
  + [2091b73] [2017-10-20] livepatch: __klp_disable_patch() should never be called for disabled patches (pmladek@suse.com)
  + [a597c53] [2017-10-20] livepatch: Correctly call klp_post_unpatch_callback() in error paths (pmladek@suse.com)
  + [1724a5d] [2017-10-13] livepatch: add transition notices (joe.lawrence@redhat.com)
  + [2056375] [2017-10-13] livepatch: move transition "complete" notice into klp_complete_transition() (joe.lawrence@redhat.com)
  + [b2f6b10] [2017-10-13] livepatch: add (un)patch callbacks (joe.lawrence@redhat.com)
  + [c993385] [2017-09-14] livepatch: __klp_shadow_get_or_alloc() is local to shadow.c (jkosina@suse.cz)
  + [ac66781] [2017-08-31] livepatch: introduce shadow variable API (joe.lawrence@redhat.com)
  + [79b3121] [2019-08-15] Partially revert cc946adcb9e983ad9fe56ebe35f1292e111ff10e (sblbir@amzn.com)
  + [6208f29] [2019-07-11] PCI: Add ACS quirk for Amazon Annapurna Labs root ports (alisaidi@amazon.com)
  + [3a186c7] [2019-07-11] PCI: Add Amazon's Annapurna Labs vendor ID (jonnyc@amazon.com)
  + [98e8874] [2019-06-24] linux/ena: update ENA linux driver to version 2.1.1 (fllinden@amazon.com)
  + [f1c841d] [2019-07-02] microvm: enable debug in case of tcp out of memory (alakeshh@amazon.com)
  + [32cc653] [2019-07-03] Fix microvm config dependency in Kconfig (alakeshh@amazon.com)
  + [cc348be] [2019-02-12] NFS: Remove redundant semicolon (zhangliguang@linux.alibaba.com)
  + [9dcb0e6] [2019-05-31] arm64: acpi/pci: invoke _DSM whether to preserve firmware PCI setup (fllinden@amazon.com)
  + [37e438a] [2019-03-28] PCI: al: Add Amazon Annapurna Labs PCIe host controller driver (jonnyc@amazon.com)
  + [fde252f] [2019-04-24] irqchip/gic-v2m: invoke from gic-v3 initialization and add acpi quirk flow (zeev@amazon.com)
  + [bc8efec] [2019-04-03] lustre: fix ACL handling (fllinden@amazon.com)
  + [6afbaec] [2018-05-18] x86/stacktrace: Enable HAVE_RELIABLE_STACKTRACE for the ORC unwinder (jslaby@suse.cz)
  + [5aa67ef] [2018-05-18] x86/unwind/orc: Detect the end of the stack (jpoimboe@redhat.com)
  + [253596e] [2018-05-18] x86/stacktrace: Do not fail for ORC with regs on stack (jslaby@suse.cz)
  + [540a9a3] [2018-05-18] x86/stacktrace: Clarify the reliable success paths (jslaby@suse.cz)
  + [b4324c0] [2018-05-18] x86/stacktrace: Remove STACKTRACE_DUMP_ONCE (jslaby@suse.cz)
  + [947a0c1] [2018-05-18] x86/stacktrace: Do not unwind after user regs (jslaby@suse.cz)
  + [cf22e7d] [2019-03-12] Add new config CONFIG_MICROVM to enable microvm optimized kernel (alakeshh@amazon.com)
  + [43cb7ae] [2019-02-19] tcp: Namespace-ify sysctl_tcp_rmem and sysctl_tcp_wmem (edumazet@google.com)
  + [c9fd5bd7] [2017-11-07] net: allow per netns sysctl_rmem and sysctl_wmem for protos (edumazet@google.com)
  + [a7d4d7a] [2019-03-01] Config glue for lustre client. (fllinden@amazon.com)
  + [cb09ab2] [2019-03-01] Import lustre client 2.10.5 (fllinden@amazon.com)
  + [eb03791] [2018-06-05] iomap: fsync swap files before iterating mappings (darrick.wong@oracle.com)
  + [b5a0423] [2018-06-01] iomap: inline data should be an iomap type, not a flag (hch@lst.de)
  + [38352dd] [2018-05-16] iomap: don't allow holes in swapfiles (osandov@fb.com)
  + [23b4824] [2018-05-16] iomap: provide more useful errors for invalid swap files (osandov@fb.com)
  + [c517bfb] [2018-05-10] iomap: add a swapfile activation function (darrick.wong@oracle.com)
  + [29c5730] [2019-01-30] xfs, iomap: define and use the IOMAP_F_DIRTY flag in xfs (fllinden@amazon.com)
  + [f406734] [2018-08-01] xfs: only validate summary counts on primary superblock (darrick.wong@oracle.com)
  + [2d88292] [2018-07-26] libxfs: add more bounds checking to sb sanity checks (billodo@redhat.com)
  + [8f13271] [2018-07-29] xfs: refactor superblock verifiers (darrick.wong@oracle.com)
  + [421e022] [2019-01-31] xen-netfront: call netif_device_attach on resume (fllinden@amazon.com)
  + [6b83878] [2018-10-04] ACPI/PPTT: Handle architecturally unknown cache types (jhugo@codeaurora.org)
  + [40d0da6] [2018-06-05] ACPI / PPTT: fix build when CONFIG_ACPI_PPTT is not enabled (sudeep.holla@arm.com)
  + [a771435] [2018-06-29] ACPI / PPTT: use ACPI ID whenever ACPI_PPTT_ACPI_PROCESSOR_ID_VALID is set (Sudeep.Holla@arm.com)
  + [f9480d5] [2018-05-11] arm64: topology: divorce MC scheduling domain from core_siblings (jeremy.linton@arm.com)
  + [588a6ac] [2018-05-11] ACPI: Add PPTT to injectable table list (jeremy.linton@arm.com)
  + [4a6bbd0] [2018-05-11] arm64: topology: enable ACPI/PPTT based CPU topology (jeremy.linton@arm.com)
  + [83cef7f] [2018-05-11] arm64: topology: rename cluster_id (jeremy.linton@arm.com)
  + [adc6b82] [2018-05-11] arm64: Add support for ACPI based firmware tables (jeremy.linton@arm.com)
  + [24d5981] [2018-05-11] drivers: base cacheinfo: Add support for ACPI based firmware tables (jeremy.linton@arm.com)
  + [9a17877] [2018-05-11] ACPI: Enable PPTT support on ARM64 (jeremy.linton@arm.com)
  + [5be3338] [2018-05-11] ACPI/PPTT: Add Processor Properties Topology Table parsing (jeremy.linton@arm.com)
  + [253e20b] [2018-05-11] arm64/acpi: Create arch specific cpu to acpi id helper (jeremy.linton@arm.com)
  + [0023103] [2018-05-11] cacheinfo: rename of_node to fw_token (jeremy.linton@arm.com)
  + [be9b9b4] [2018-05-11] drivers: base: cacheinfo: setup DT cache properties early (jeremy.linton@arm.com)
  + [ea16db6] [2018-05-11] drivers: base: cacheinfo: move cache_setup_of_node() (jeremy.linton@arm.com)
  + [13dcbf5] [2017-11-17] ACPICA: ACPI 6.2: Additional PPTT flags (jeremy.linton@arm.com)
  + [bff52c8] [2018-07-23] arm64: acpi: fix alignment fault in accessing ACPI (takahiro.akashi@linaro.org)
  + [7be244c] [2018-07-02] arm64: kexec: always reset to EL2 if present (mark.rutland@arm.com)
  + [4abaa4c] [2018-03-08] efi/arm64: Check whether x18 is preserved by runtime services calls (ard.biesheuvel@linaro.org)
  + [4304102] [2018-10-11] arm64: Fix /proc/iomem for reserved but not memory regions (will.deacon@arm.com)
  + [7a5bf0c] [2018-07-23] arm64: export memblock_reserve()d regions via /proc/iomem (james.morse@arm.com)
  + [13f14c6] [2018-11-10] net: ena: Import the ENA v2 driver (2.0.2g) (alakeshh@amazon.com)
  + [c3f63a2] [2018-11-10] xen: Only restore the ACPI SCI interrupt in xen_restore_pirqs. (fllinden@amazon.com)
  + [eb72a07] [2018-10-26] xen: restore pirqs on resume from hibernation. (fllinden@amazon.com)
  + [b2e2788] [2018-10-29] ACPICA: Enable sleep button on ACPI legacy wake (anchalag@amazon.com)
  + [92c1bbf] [2018-10-18] block: xen-blkfront: consider new dom0 features on restore (eduval@amazon.com)
  + [be6e59c] [2017-11-30] vmxnet3: increase default rx ring sizes (skhare@vmware.com)
  + [7c7073f] [2018-04-27] x86/CPU/AMD: Derive CPU topology from CPUID function 0xB when available (suravee.suthikulpanit@amd.com)
  + [02ca47a] [2017-09-07] sched/topology: Introduce NUMA identity node sched domain (suravee.suthikulpanit@amd.com)
  + [85454968] [2018-06-13] x86/CPU/AMD: Fix LLC ID bit-shift calculation (suravee.suthikulpanit@amd.com)
  + [8a89947] [2018-04-27] x86/CPU/AMD: Calculate last level cache ID from number of sharing threads (suravee.suthikulpanit@amd.com)
  + [b646178] [2018-04-27] x86/CPU: Rename intel_cacheinfo.c to cacheinfo.c (bp@suse.de)
  + [e33c3e3] [2018-05-17] x86/MCE/AMD: Read MCx_MISC block addresses on any CPU (bp@suse.de)
  + [9d36264] [2018-08-15] blk-wbt: Avoid lock contention and thundering herd issue in wbt_wait (anchalag@amazon.com)
  + [5141c4a] [2018-01-12] blk-mq: simplify queue mapping & schedule with each possisble CPU (hch@lst.de)
  + [504a76b] [2018-04-09] x86: tsc: avoid system instability in hibernation (eduval@amazon.com)
  + [0497577] [2018-06-05] xen-blkfront: Fixed blkfront_restore to remove a call to negotiate_mq (anchalag@amazon.com)
  + [904f750] [2018-03-24] KVM: X86: Fix setup the virt_spin_lock_key before static key get initialized (wanpengli@tencent.com)
  + [718f937] [2017-10-28] x86/paravirt: Set up the virt_spin_lock_key after static keys get initialized (douly.fnst@cn.fujitsu.com)
  + [1dcda19] [2018-02-13] KVM: X86: Choose qspinlock when dedicated physical CPUs are available (wanpengli@tencent.com)
  + [ed99609] [2018-02-13] KVM: Introduce paravirtualization hints and KVM_HINTS_DEDICATED (wanpengli@tencent.com)
  + [ea9f0ba] [2017-09-06] locking/paravirt: Use new static key for controlling call of virt_spin_lock() (jgross@suse.com)
  + [5e38bc4] [2018-03-27] Revert "xen: dont fiddle with event channel masking in suspend/resume" (anchalag@amazon.com)
  + [30f3670] [2018-01-18] ACPI: SPCR: Make SPCR available to x86 (prarit@redhat.com)
  + [aa34040] [2016-04-26] xen-blkfront: add 'persistent_grants' parameter (aliguori@amazon.com)
  + [0a99d07] [2017-03-10] xen-blkfront: resurrect request-based mode (kamatam@amazon.com)
  + [e9b525e] [2017-11-02] Not-for-upstream: PM / hibernate: Speed up hibernation by batching requests (cyberax@amazon.com)
  + [878e723] [2017-10-27] PM / hibernate: update the resume offset on SNAPSHOT_SET_SWAP_AREA (cyberax@amazon.com)
  + [230d7b0] [2017-08-24] x86/xen: close event channels for PIRQs in system core suspend callback (kamatam@amazon.com)
  + [7e48fcb] [2017-08-24] xen/events: add xen_shutdown_pirqs helper function (kamatam@amazon.com)
  + [ca36e7d] [2017-07-21] x86/xen: save and restore steal clock (kamatam@amazon.com)
  + [b60256e] [2017-07-13] xen/time: introduce xen_{save,restore}_steal_clock (kamatam@amazon.com)
  + [598810c] [2017-01-09] xen-netfront: add callbacks for PM suspend and hibernation support (kamatam@amazon.com)
  + [5225ad3] [2017-06-08] xen-blkfront: add callbacks for PM suspend and hibernation (kamatam@amazon.com)
  + [4b28881] [2017-02-11] x86/xen: add system core suspend and resume callbacks (kamatam@amazon.com)
  + [fe741a9] [2018-02-22] x86/xen: Introduce new function to map HYPERVISOR_shared_info on Resume (anchalag@amazon.com)
  + [18e11e1] [2017-07-13] xenbus: add freeze/thaw/restore callbacks support (kamatam@amazon.com)
  + [fb41e0a] [2017-07-13] xen/manage: introduce helper function to know the on-going suspend mode (kamatam@amazon.com)
  + [e6bea3b] [2017-07-12] xen/manage: keep track of the on-going suspend mode (kamatam@amazon.com)
  + [2d7d2d9] [2018-02-27] Importing Amazon ENA driver 1.5.0 into amazon-4.14.y/master. (vallish@amazon.com)
  + [1954f5b] [2018-02-12] drivers/amazon: introduce AMAZON_ENA_ETHERNET (vallish@amazon.com)
  + [b722e574] [2018-02-12] drivers/amazon: add network device drivers support (vallish@amazon.com)
  + [84dc5da] [2018-02-12] drivers: introduce AMAZON_DRIVER_UPDATES (vallish@amazon.com)
  + [9d0a089] [2017-10-27] not-for-upstream: testmgr config changes to enable FIPS boot (alakeshh@amazon.com)
  + [8f4d880] [2017-09-19] nvme: update timeout module parameter type (vallish@amazon.com)
  + [16fcbe4] [2015-12-08] force perf to use /usr/bin/python instead of /usr/bin/python2 (kamatam@amazon.com)
  + [831695f] [2013-02-13] bump default tcp_wmem from 16KB to 20KB (gafton@amazon.com)
  + [6d09692] [2016-01-26] bump the default TTL to 255 (kamatam@amazon.com)
  + [d2e7a1d] [2012-02-10] scsi: sd_revalidate_disk prevent NULL ptr deref (kernel-team@fedoraproject.org)
  + [cc42730] [2008-10-06] kbuild: AFTER_LINK (roland@redhat.com)


