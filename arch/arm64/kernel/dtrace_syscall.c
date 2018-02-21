/*
 * FILE:	dtrace_syscall.c
 * DESCRIPTION:	Dynamic Tracing: system call tracing support (arch-specific)
 *
 * Copyright (C) 2010-2014 Oracle Corporation
 */

#include <linux/dtrace_syscall.h>
#include <linux/ptrace.h>
#include <asm/syscall.h>

void (*systrace_probe)(dtrace_id_t, uintptr_t, uintptr_t, uintptr_t, uintptr_t,
		       uintptr_t, uintptr_t, uintptr_t);

void systrace_stub(dtrace_id_t id, uintptr_t arg0, uintptr_t arg1,
		   uintptr_t arg2, uintptr_t arg3, uintptr_t arg4,
		   uintptr_t arg5, uintptr_t arg6)
{
}

asmlinkage long systrace_syscall(uintptr_t, uintptr_t, uintptr_t, uintptr_t,
				 uintptr_t, uintptr_t, uintptr_t);

static systrace_info_t	systrace_info = {
				&systrace_probe,
				systrace_stub,
				systrace_syscall,
				{
#define DTRACE_SYSCALL_STUB(id, name) \
				[SCE_##id] (dt_sys_call_t)dtrace_stub_##name,
#include <asm/dtrace_syscall.h>
#undef DTRACE_SYSCALL_STUB
				},
				{
#undef __SYSCALL
#define __SYSCALL(nr, sym)	[nr] { .name = __stringify(sym), },
#include <asm/unistd.h>
#undef __SYSCALL
				}
			};


asmlinkage long systrace_syscall(uintptr_t arg0, uintptr_t arg1,
				 uintptr_t arg2, uintptr_t arg3,
				 uintptr_t arg4, uintptr_t arg5,
				 uintptr_t arg6)
{
	long			rc = 0;
	unsigned long		sysnum;
	dtrace_id_t		id;
	dtrace_syscalls_t	*sc;

	sysnum = syscall_get_nr(current, current_pt_regs());
	sc = &systrace_info.sysent[sysnum];

	id = sc->stsy_entry;
	if (id != DTRACE_IDNONE)
		(*systrace_probe)(id, arg0, arg1, arg2, arg3, arg4, arg5,
				  arg6);

	/*
	 * FIXME: Add stop functionality for DTrace.
	 */

	if (sc->stsy_underlying != NULL)
		rc = (*sc->stsy_underlying)(arg0, arg1, arg2, arg3, arg4,
					    arg5, arg6);

	id = sc->stsy_return;
	if (id != DTRACE_IDNONE)
		(*systrace_probe)(id, (uintptr_t)rc, (uintptr_t)rc,
				  (uintptr_t)((uint64_t)rc >> 32), 0, 0, 0, 0);

	return rc;
}

systrace_info_t *dtrace_syscalls_init()
{
	int			i;

	/*
	 * Only initialize this stuff once...
	 */
	if (systrace_info.sysent[0].stsy_tblent != NULL)
		return &systrace_info;

	for (i = 0; i < NR_syscalls; i++) {
		systrace_info.sysent[i].stsy_tblent =
					(dt_sys_call_t *)&sys_call_table[i];
		systrace_info.sysent[i].stsy_underlying =
					(dt_sys_call_t)sys_call_table[i];
	}

	return &systrace_info;
}
EXPORT_SYMBOL(dtrace_syscalls_init);
