#
# Makefile for inverting MT data using Occam1D.
# Written by Bo Yang, SES, ZJU, 2022/05/04.
#
#.SECONDARY:
include png.list

all: $(png)

%.png: edi/%.ztab
	site=`basename $@ .png`; \
	mkdir $$site; \
	cp mk.para $$site; \
	cp $< mkpara.sh $$site; \
	cp Makefile_1DMTOCC $$site/Makefile; \
	cd $$site; \
	./mkpara.sh $$site; \
	make;

edi/%.ztab: edi/%.edi
	edi2ztab.sh $<
	site=`basename $@ .ztab`; \
	mv $$site.ztab edi/
