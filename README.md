# qpAdm_wrapper
A wrapper to estimate admixture proportions and test ancestry models using qpAdm (https://github.com/DReichLab/AdmixTools, requires AdmixTools).

Example input:
```
python2 qpadm_wrapper.py --file GENOTYPE_FILE --target ADMIXED_POP --sources NUMBER --references REF1,REF2,REF3,REF4,REF5 --temppath PATH_TO_TEMPORARY_FILES
```
The wrapper will cycle through all NUMBER-wise combinations of the reference populations as sources [1, 2, 3 or maximum 4 is recommended]. 
Alternatively, a specific set of populations (1, 2, 3 or 4) can be given as the --sources argument, in which case the wrapper will only run qpAdm for that model only.

The output is organised in tab-separated columns:
1. Target population
2. Source population
3. Reference populations. Note that the first listed is BASE, and used to obtain many f-statistics in computations.
4. P-value for the admixture model
5. Estimated admixture proportions. Comma-separated, in the same order as source populations were given
6. Standard errors for the estimated admixture proportions
7. Number of SNPs used by qpAdm
8. The reference population that results in the largest absolute Z-score for statistics of the form f4(Target,Fitted_target; BASE, Reference). Obtained from the "details" mode of qpAdm. This can provide hints on how to improve the list of references.

A useful feature is that populations can be pooled on-the-fly on the command line by a + sign between them (see Ju_hoan_North.DG+Khomani_San.DG) in the example below.

Here is an example of usage where we estimate Denisovan ancestry in Papuan genomes using freely available data for 1.2M SNPs from the Reich lab (https://reich.hms.harvard.edu/downloadable-genotypes-present-day-and-ancient-dna-data-compiled-published-papers). Out of 28 possible pairs of a set of 9 reference populations, only 1 model fits the data, which is that Papuan genomes have ancestry related both to East Asia (approximated by Japanese in the model) and Denisovans (Siberian Denisovans in the model).

See comments on each of the three model tests in the right margin.

```
python2 qpadm_wrapper.py --file v42.4.1240K --target Papuan.DG --sources 2 --outgroups Japanese.DG,Denisova.DG,Dinka.DG,Mbuti.DG,Ju_hoan_North.DG+Khomani_San.DG,Altai_Neanderthal.DG,Vindija.DG,Chimp.REF | cut -f 2,4- | sort -rgk2 | head -n3
28 combinations
	
Japanese.DG,Denisova.DG 	0.0636580648 	0.971,0.029 		0.003,0.003 	1015825 	Mbuti.DG -1.484593 		#The only model that fits (P=0.06) estimates 2.9% +/- 0.3% Denisovan ancestry
Altai_Neanderthal.DG,Vindija.DG 0.0275054402 	-271.122,272.122 	70.061,70.061 	1018748 	Ju_hoan_North.DG 0.736495 	#The model with the second largest p-value has unreasonable admixture proportions (27200% and -27200% from each of two Neanderthals), and can be excluded
Japanese.DG,Chimp.REF 		0.00601963502 	0.943,0.057 		0.005,0.005 	1031376 	Altai_Neanderthal.DG 2.722215 	#This model has a very low p-value (0.006) so can be rejected, but fits the archaic admixture as being from the outgroup chimpanzee. We can see that the largest outlier statistic f4(Target, Fitted_target; BASE, Reference) is f4(Papuan,Fitted_Papuan; Denisova, Altai_Neandertal), Z=2.72 suggests that there is undermodelled affinity between the Denisovan (which is BASE here) and empirical Papuan genomes, compared to the fitted Papuan allele frequencies.

```

For testing a single model:

```
python2 qpadm_wrapper.py --file v42.4.1240K --target Papuan.DG --sources Japanese.DG,Denisova.DG --outgroups Dinka.DG,Mbuti.DG,Ju_hoan_North.DG+Khomani_San.DG,Altai_Neanderthal.DG,Vindija.DG,Chimp.REF | cut -f 2,4-

Japanese.DG,Denisova.DG 	0.0636580648 	0.971,0.029 		0.003,0.003 	1015825 	Mbuti.DG -1.484593

```

For more options, including specifying path to admixtools, see
```
python2 qpadm_wrapper.py --help
Usage: qpadm_wrapper.py [options] arg1 arg2

Options:
  -h, --help            show this help message and exit
  --target=TARGET       target
  --sources=SOURCES     sources
  --references=REFERENCES
                        list of reference populations
  --outgroups=OUTGROUPS
                        list of outgroups (synonymous with --references)
  --file=FILE           file
  --indfile=INDFILE     indfile
  --temppath=TEMPPATH   path for temporary input and output files
  --locus=LOCUS         locus
  --snplist=SNPLIST     .snp file with subset of SNPs to use
  --chromosome=CHROMOSOME
                        chromosome
  --numchrom=NUMCHROM   numchrom
  --plink               plink
  --details             details
  --qpwave              qpwave
  --fulloutput          fulloutput
  --outfile=OUTFILE     outfile
```

This tool is provided as-is with no warrenty, and is not under continual user support.
