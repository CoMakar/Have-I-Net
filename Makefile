include .env

pyi=pipenv run pyinstaller

build:
	$(pyi) main.spec

pack:
	if not exist .versions mkdir .versions
	tar -cvf "./.versions/Have_I-Net_Win10_x64_v$(BUILD_VERSION).zip" -C "./dist/" "haveinet.exe"

.PHONY:	build