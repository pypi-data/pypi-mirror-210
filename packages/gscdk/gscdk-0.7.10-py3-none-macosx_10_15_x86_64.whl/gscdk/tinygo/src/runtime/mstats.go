package runtime

// Memory statistics

// Subset of memory statistics from upstream Go.
// Works with conservative gc only.

// A MemStats records statistics about the memory allocator.
type MemStats struct {
	// General statistics.

	// Sys is the total bytes of memory obtained from the OS.
	//
	// Sys is the sum of the XSys fields below. Sys measures the
	// address space reserved by the runtime for the
	// heap, stacks, and other internal data structures.
	Sys uint64

	// Heap memory statistics.

	// HeapSys is bytes of heap memory, total.
	//
	// In TinyGo unlike upstream Go, we make no distinction between
	// regular heap blocks used by escaped-to-the-heap variables and
	// blocks occupied by goroutine stacks,
	// all such blocks are marked as in-use, see HeapInuse below.
	HeapSys uint64

	// HeapIdle is bytes in idle (unused) blocks.
	HeapIdle uint64

	// HeapInuse is bytes in in-use blocks.
	HeapInuse uint64

	// HeapReleased is bytes of physical memory returned to the OS.
	HeapReleased uint64

	// TotalAlloc is cumulative bytes allocated for heap objects.
	//
	// TotalAlloc increases as heap objects are allocated, but
	// unlike Alloc and HeapAlloc, it does not decrease when
	// objects are freed.
	TotalAlloc uint64

	// Mallocs is the cumulative count of heap objects allocated.
	// The number of live objects is Mallocs - Frees.
	Mallocs uint64

	// Frees is the cumulative count of heap objects freed.
	Frees uint64

	// Off-heap memory statistics.
	//
	// The following statistics measure runtime-internal
	// structures that are not allocated from heap memory (usually
	// because they are part of implementing the heap).

	// GCSys is bytes of memory in garbage collection metadata.
	GCSys uint64
}
