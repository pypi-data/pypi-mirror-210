//go:build eosio && gc.leaking
// +build eosio,gc.leaking

package runtime

/*
#include <stdlib.h>
#include <string.h>
// void *	 memset (void *, int, size_t);
void * malloc(size_t size);
*/
import "C"

// This GC implementation is the simplest useful memory allocator possible: it
// only allocates memory and never frees it. For some constrained systems, it
// may be the only memory allocator possible.

import (
	"unsafe"
)

// Ever-incrementing pointer: no memory is freed.
var heapptr = heapStart

func alloc(size uintptr, layout unsafe.Pointer) unsafe.Pointer {
	// return unsafe.Pointer(uintptr(C.malloc(C.size_t(size))))
	// TODO: this can be optimized by not casting between pointers and ints so
	// much. And by using platform-native data types (e.g. *uint8 for 8-bit
	// systems).
	size = align(size)
	addr := heapptr
	heapptr += size
	for heapptr >= heapEnd {
		// Try to increase the heap and check again.
		if growHeap() {
			continue
		}
		// Failed to make the heap bigger, so we must really be out of memory.
		runtimePanic("out of memory")
	}

	C.memset(unsafe.Pointer(addr), 0, C.size_t(size))
	// for i := uintptr(0); i < uintptr(size); i += 4 {
	// 	ptr := (*uint32)(unsafe.Pointer(addr + i))
	// 	*ptr = 0
	// }
	return unsafe.Pointer(addr)
}

func free(ptr unsafe.Pointer) {
	// Memory is never freed.
}

func GC() {
	// No-op.
}

func KeepAlive(x interface{}) {
	// Unimplemented. Only required with SetFinalizer().
}

func SetFinalizer(obj interface{}, finalizer interface{}) {
	// Unimplemented.
}

func initHeap() {
	// preinit() may have moved heapStart; reset heapptr
	ptr := heapStart
	if GOARCH == "wasm" {
		// llvm11 and llvm12 do not correctly align the heap on wasm
		ptr = align(ptr)
	}
	heapptr = ptr
}

// setHeapEnd sets a new (larger) heapEnd pointer.
func setHeapEnd(newHeapEnd uintptr) {
	// This "heap" is so simple that simply assigning a new value is good
	// enough.
	heapEnd = newHeapEnd
}

func markRoots(start, end uintptr) {
	// dummy, so that markGlobals will compile
}
