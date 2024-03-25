# Notes

## TODO List

### Done
- build llvm, den den philipp geschickt hat
	Wichtig: build lld & Clang 
	`cmake -S llvm -B build -G Ninja -DLLVM_ENABLE_PROJECTS="clang;lld" -DCMAKE_BUILD_TYPE=Release`
- install dir ändern
	? weiß nicht was ich damit meinte
	wahrscheinlich den path zu llvm/etiss, also erledigt, geht auch ohne make/ninja install	
- schauen das der verwendete etiss passt
	anpassbar mit dem path zu run_helper.sh
- schauen ob der command von philipp durchläuft
	Läuft, nachdem ich lld noch compiled habe

### TODO


## Notes

LLVM und ETISS in mloncmu festlegen 
> den path zu etiss und llvm kannst du auf der cmdline überschreiben
> -c llvm.install_dir=/path/to/lllvm sowie -c etissvp.script=/path/to/run_helper.sh




## Commands

Main mlonmcu flow to run an compare benchmarks with and without the extensions

    $ python3 -m mlonmcu.cli.main flow run coremark --target etiss -c mlif.toolchain=llvm -c mlif.extend_attrs=1 --config-gen mlif.global_isel=1 --post config2cols -c config2cols.limit=mlif.global_isel,auto_vectorize.custom_unroll -v --parallel -c llvm.install_dir=/home/cecil/Documents/llvm-project/build/ --post analyse_dump --post rename_cols -c rename_cols.mapping="{'config_mlif.global_isel':'GIsel','config_auto_vectorize.custom_unroll':'Unroll'}" --post filter_cols -c filter_cols.keep="Model,ROM code,GIsel,Reason,DumpCountsGen,Total Instructions,Unroll" -c mlif.strip_strings=0 -c analyse_dump.to_df=1  -c etissvp.script=/home/cecil/Documents/etissVK/build/installed/bin/run_helper.sh --post compare_rows -f auto_vectorize --config-gen3 auto_vectorize.custom_unroll=1 --config-gen2 etiss.attr="+m" --config-gen2 etiss.attr="+m,+xseal5testalucvabs16,+xseal5testalucvabs32,+xseal5testalucvabs8,+xseal5testalucvaddnrsi16,+xseal5testalucvaddnrsi32,+xseal5testalucvaddnrui16,+xseal5testalucvaddnrui32,+xseal5testalucvaddns,+xseal5testalucvaddnu,+xseal5testalucvaddrnrsi16,+xseal5testalucvaddrnrsi32,+xseal5testalucvaddrnrui16,+xseal5testalucvaddrnrui32,+xseal5testalucvaddrns,+xseal5testalucvaddrnu,+xseal5testalucvextbs,+xseal5testalucvextbz,+xseal5testalucvexths,+xseal5testalucvexthz,+xseal5testalucvmaxi1216,+xseal5testalucvmaxi1232,+xseal5testalucvmaxi516,+xseal5testalucvmaxi532,+xseal5testalucvmaxs16,+xseal5testalucvmaxs32,+xseal5testalucvmaxs8,+xseal5testalucvmaxu16,+xseal5testalucvmaxu32,+xseal5testalucvmaxu8,+xseal5testalucvmini1216,+xseal5testalucvmini1232,+xseal5testalucvmini516,+xseal5testalucvmini532,+xseal5testalucvmins16,+xseal5testalucvmins32,+xseal5testalucvmins8,+xseal5testalucvminu16,+xseal5testalucvminu32,+xseal5testalucvminu8,+xseal5testalucvsletsi16,+xseal5testalucvsletsi32,+xseal5testalucvsletui16,+xseal5testalucvsletui32,+xseal5testalucvsubnrsi16,+xseal5testalucvsubnrsi32,+xseal5testalucvsubnrui16,+xseal5testalucvsubnrui32,+xseal5testalucvsubns,+xseal5testalucvsubnu,+xseal5testalucvsubrnrsi16,+xseal5testalucvsubrnrsi32,+xseal5testalucvsubrnrui16,+xseal5testalucvsubrnrui32,+xseal5testalucvsubrns,+xseal5testalucvsubrnu,+xseal5testmaccvmachhns,+xseal5testmaccvmachhnu,+xseal5testmaccvmachhrns,+xseal5testmaccvmachhrnu,+xseal5testmaccvmacns,+xseal5testmaccvmacnu,+xseal5testmaccvmacrns,+xseal5testmaccvmacrnu,+xseal5testmaccvmacsi16,+xseal5testmaccvmacsi32,+xseal5testmaccvmacui16,+xseal5testmaccvmacui32,+xseal5testmaccvmsusi16,+xseal5testmaccvmsusi32,+xseal5testmaccvmsuui16,+xseal5testmaccvmsuui32,+xseal5testmaccvmulhhns,+xseal5testmaccvmulhhnu,+xseal5testmaccvmulhhrns,+xseal5testmaccvmulhhrnu,+xseal5testmaccvmulns,+xseal5testmaccvmulnu,+xseal5testmaccvmulrns,+xseal5testmaccvmulrnu,+grp32v"
