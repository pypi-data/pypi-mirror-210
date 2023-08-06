//go:build (avr && atmega328p) || arduino || arduino_nano
// +build avr,atmega328p arduino arduino_nano

package machine

const (
	// Note: start at port B because there is no port A.
	portB Pin = iota * 8
	portC
	portD
)

const (
	PB0 = portB + 0
	PB1 = portB + 1 // peripherals: Timer1 channel A
	PB2 = portB + 2 // peripherals: Timer1 channel B
	PB3 = portB + 3 // peripherals: Timer2 channel A
	PB4 = portB + 4
	PB5 = portB + 5
	PB6 = portB + 6
	PB7 = portB + 7
	PC0 = portC + 0
	PC1 = portC + 1
	PC2 = portC + 2
	PC3 = portC + 3
	PC4 = portC + 4
	PC5 = portC + 5
	PC6 = portC + 6
	PC7 = portC + 7
	PD0 = portD + 0
	PD1 = portD + 1
	PD2 = portD + 2
	PD3 = portD + 3 // peripherals: Timer2 channel B
	PD4 = portD + 4
	PD5 = portD + 5 // peripherals: Timer0 channel B
	PD6 = portD + 6 // peripherals: Timer0 channel A
	PD7 = portD + 7
)
