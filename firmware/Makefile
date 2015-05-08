PROJECT_NAME = spectrumwars
PROJECT_SOURCES = main.c vsndriversconf.c
PROJECT_HEADERS = vsndriversconf.h

VESNALIB_LOCATION=../../../vesna-drivers

include $(VESNALIB_LOCATION)/Makefile.vesnadrivers

install: $(PROJECT_NAME).load5
	echo "firmware loaded"
