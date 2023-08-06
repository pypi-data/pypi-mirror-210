//go:build baremetal || wasi || wasm || eosio
// +build baremetal wasi wasm eosio

// This file emulates some process-related functions that are only available
// under a real operating system.

package syscall

func Getuid() int  { return -1 }
func Geteuid() int { return -1 }
func Getgid() int  { return -1 }
func Getegid() int { return -1 }
func Getpid() int  { return -1 }
func Getppid() int { return -1 }
