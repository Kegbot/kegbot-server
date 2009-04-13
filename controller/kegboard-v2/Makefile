default:
	jal kegboard.jal

clean:
	rm -f kegboard.hex kegboard.asm 

program: default
	sudo odyssey PIC16F628A erase
	sudo odyssey PIC16F628A write kegboard.hex
