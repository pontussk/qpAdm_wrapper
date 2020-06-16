import sys
import subprocess
import itertools
from optparse import OptionParser
import random

usage = "usage: %prog [options] arg1 arg2"
parser = OptionParser(usage=usage)
parser.add_option("--target", action="store", type="string", dest="target",help="target")
parser.add_option("--sources", action="store", type="string", dest="sources",help="sources",default='sources')
parser.add_option("--references", action="store",type="string", dest="references",help="list of reference populations",default=False)
parser.add_option("--outgroups", action="store",type="string", dest="outgroups",help="list of outgroups (synonymous with --references)",default=False)
parser.add_option("--file", action="store",type="string", dest="file",help="file")
parser.add_option("--indfile", action="store",type="string", dest="indfile",help="indfile",default=False)
parser.add_option("--temppath", action="store",type="string", dest="temppath",help="path for temporary input and output files",default="/camp/lab/skoglundp/scratch/stats/")
parser.add_option("--locus", action="store", dest="locus",help="locus",default=False)
parser.add_option("--snplist", action="store",type="string", dest="snplist",help=".snp file with subset of SNPs to use",default=False)
parser.add_option("--chromosome", action="store", dest="chromosome",help="chromosome",default=False)
parser.add_option("--numchrom", action="store", dest="numchrom",help="numchrom",default=False)
parser.add_option("--scan", action="store_true", dest="scan",help="scan",default=False)
parser.add_option("--plink", action="store_true", dest="plink",help="plink",default=False)
parser.add_option("--windowsize", action="store",type="int", dest="windowsize",help="windowsize",default=False)
parser.add_option("--stepsize", action="store",type="int", dest="stepsize",help="stepsize",default=False)
parser.add_option("--details", action="store_true", dest="details",help="details",default=False)
parser.add_option("--qpwave", action="store_true", dest="qpwave",help="qpwave",default=False)
parser.add_option("--fulloutput", action="store_true", dest="fulloutput",help="fulloutput",default=False)
parser.add_option("--outfile", action="store",type="string", dest="outfile",help="outfile",default=False)
(options, args) = parser.parse_args()

tempname=str(random.randint(0,1000000000000))

#/home/sm213/work/temp_other_peeps/for_ps/pt2hs.fa
if options.references != False:
	options.outgroups=options.references

target=options.target
sources=options.sources.split(',')
alloutgroups=options.outgroups.split(',')
alloutgroups=[a for a in alloutgroups if a !=target]

if options.outfile != False:
	sys.stdout = open(options.outfile, 'w')
	
if options.indfile == False:
	options.indfile=options.file
	
if options.indfile == True:
	options.indfile=options.indfile.rstrip('.ind')

fullpops=sources+alloutgroups
fullpops.append(target)
#print fullpops

if '+' in '_'.join(fullpops):
	newinddata=[]
	for line in open(options.indfile+'.ind'):
		col=line.split()
		if options.plink:
			newpop=col[0]
		else:
			newpop=col[2]
		for pop in fullpops:
			if '+' in pop:
				sepop=pop.split('+')
				if newpop in sepop:
					newpop=sepop[0]

		if options.plink:
			newindline=' '.join([newpop]+col[1:])
			newinddata.append(newindline)
			#print newindline
		else:
			newindline=' '.join(col[0:2]+[newpop])
			newinddata.append(newindline)
			#print newindline

	newindfilename=options.temppath+tempname
	options.indfile=newindfilename
	newindfile=open(newindfilename+'.ind', 'w')
	newindfile.write('\n'.join(newinddata))
	newindfile.close()
	
	#now also change the right and left pops
	target=target.split('+')[0]
	sources=[t.split('+')[0] for t in sources]
	alloutgroups=[t.split('+')[0] for t in alloutgroups]
	#print target,sources, alloutgroups
	options.sources=sources


if options.sources[0].isdigit():
	sourcelist=list(itertools.combinations(alloutgroups, int(sources[0])))
	print >>sys.stderr,len(sourcelist),'combinations'
else:
	sourcelist=[sources]


chrlendict={'1':249250621,
'2':243199373,
'3':198022430,
'4':191154276,
'5':180915260,
'6':171115067,
'7':159138663,
'8':146364022,
'9':141213431,
'10':135534747,
'11':135006516,
'12':133851895,
'13':115169878,
'14':107349540,
'15':102531392,
'16':90354753,
'17':81195210,
'18':78077248,
'19':59128983,
'20':63025520,
'21':48129895,
'22':51304566,
'23':155270560,
}


if options.snplist != False:
	import gzip
	#qpadm supports a badsnpname of list to exclude, so we collect all SNPs in the data that are not in the specified SNP list
	snplist=[]
	for line in gzip.open(options.snplist):
		col=line.split()
		if ':' in col[0]: # for Neale lab gwas files
			chromosome=col[0].split(':')[0]
			position=col[0].split(':')[1]
			name=chromosome+'_'+position
		else:
			chromosome=col[0]
			position=col[1]
			name=chromosome+'_'+position
		snplist.append(name)

	badsnplist=[]
	if options.plink:
		snpfilename=options.file+'.bim'
		for line in open(snpfilename):
			col=line.split()
			chromosome=col[0]
			position=col[3]
			snpid=chromosome+'_'+position
			
			if snpid not in snplist:
				rsid=col[1]
				badsnplist.append(rsid.rstrip('\n'))
	else:
		snpfilename=options.file+'.snp'
		for line in open(snpfilename):
			col=line.split()
			chromosome=col[0]
			position=col[3]
			snpid=chromosome+'_'+position
			
			if snpid not in snplist:
				rsid=col[0]
				badsnplist.append(rsid.rstrip('\n'))
	print len(badsnplist)
	badsnpname=options.temppath+tempname+'.'+'badsnp'
	badfile=open(badsnpname, 'w')
	badfile.write('\n'.join(badsnplist))
	badfile.close()



props=[]

outgroups=[]
outgroups+=alloutgroups
for sources in sourcelist:
	outgroups=[o for o in alloutgroups if o not in sources]
	
	leftfilename=options.temppath+tempname+'.'+'left'
	leftfile=open(leftfilename, 'w')
	leftfile.write(target+'\n'+'\n'.join(sources))
	leftfile.close()
	
	rightfilename=options.temppath+tempname+'.'+'right'
	rightfile=open(rightfilename, 'w')
	rightfile.write('\n'.join(outgroups))
	rightfile.close()

	if options.scan != False:
		chromlist=range(1,23)
		if options.chromosome !=False:
			chromlist=[int(options.chromosome)]
		for chromosome in chromlist:
			chromosome=str(chromosome)
			for start in xrange(1,int(chrlendict[chromosome]),int(options.stepsize)):
				end=start+int(options.windowsize)
				lopos=str(start)
				hipos=str(end)
				parfilename=options.temppath+tempname+'.par'
				parfile=open(parfilename, 'w')
				if options.plink:
					parfile.write("indivname:  "+options.indfile+'.fam'+'\n')
					parfile.write("snpname:  "+options.file+'.bim'+'\n')
					parfile.write("genotypename:  "+options.file+'.bed'+'\n')
				else:	
					parfile.write("indivname:  "+options.indfile+'.ind'+'\n')
					parfile.write("snpname:  "+options.file+'.snp'+'\n')
					parfile.write("genotypename:  "+options.file+'.geno'+'\n')
				parfile.write("popleft:  "+leftfilename+'\n')
				parfile.write("popright:  "+rightfilename+'\n')
				parfile.write('jackknife:  NO'+'\n')
				parfile.write('minsnps:  10'+'\n')
				parfile.write('blgsize:  0.001'+'\n')#in morgans so 0.1 cM or 100kb

				parfile.write('chrom:  '+chromosome+'\n')
				parfile.write('lopos:  '+lopos+'\n')
				parfile.write('hipos:  '+hipos+'\n')
				parfile.close()
				#this is copied from the main function below, should put this into a function
				FNULL = open('/dev/null', 'w')
				FNULL=open('temp','w')
				cmd_line=['qpAdm','-p',parfilename]
				outp_file=subprocess.Popen(cmd_line, stdout=subprocess.PIPE,stderr=FNULL)

				pileupline = outp_file.stdout.readlines()
				if options.fulloutput:
					fullout= '\n'.join([line.rstrip('\n') for line in pileupline ])
					print fullout
				for line in pileupline:
					col=line.split()
					
					#print line
					if 'coefficients:' in line:
						props=col[2:]
					if 'std. errors:' in line:
						SEs=col[2:]
					if 'numsnps used:' in line:
						numsnps=col[2]
				#print chromosome,str(start),str(end),props[0],props[1],numsnps
				try:
					print '\t'.join([chromosome,str(start),str(end),props[0],props[1],numsnps])
					props=[]
				except IndexError:
					print '\t'.join([chromosome,str(start),str(end),'NA','NA','NA'])
		exit(0)


	parfilename=options.temppath+tempname+'.par'
	parfile=open(parfilename, 'w')
	if options.plink:
		parfile.write("indivname:  "+options.indfile+'.fam'+'\n')
		parfile.write("snpname:  "+options.file+'.bim'+'\n')
		parfile.write("genotypename:  "+options.file+'.bed'+'\n')
	else:	
		parfile.write("indivname:  "+options.indfile+'.ind'+'\n')
		parfile.write("snpname:  "+options.file+'.snp'+'\n')
		parfile.write("genotypename:  "+options.file+'.geno'+'\n')
	parfile.write("popleft:  "+leftfilename+'\n')
	parfile.write("popright:  "+rightfilename+'\n')
	if options.snplist != False:
		parfile.write("badsnpname:  "+badsnpname+'\n')
	if options.details:
		parfile.write('details:  YES'+'\n')
	if options.locus != False:
		chromosome=options.locus.split(':')[0]
		parfile.write('jackknife:  NO'+'\n')
		parfile.write('chrom:  '+chromosome+'\n')
		if ':' in options.locus:
			lopos=options.locus.split(':')[1].split('-')[0]
			hipos=options.locus.split(':')[1].split('-')[1]
			parfile.write('lopos:  '+lopos+'\n')
			parfile.write('hipos:  '+hipos+'\n')

	parfile.close()

	FNULL = open('/dev/null', 'w')
	FNULL=open('temp','w')
	if options.qpwave:
		cmd_line=['qpWave','-p',parfilename]
	else:
		cmd_line=['qpAdm','-p',parfilename]
	outp_file=subprocess.Popen(cmd_line, stdout=subprocess.PIPE,stderr=FNULL)
	pileupline = outp_file.stdout.readlines()

	pvals=[]
	dscores=[]
	if options.fulloutput:
		for line in pileupline:
			print line,
	elif options.qpwave:
		for line in pileupline:
			col=line.split()
			if 'coefficients:' in line:
				props=col[2:]
			if 'std. errors:' in line:
				SEs=col[2:]
			if 'f4rank' in line:
				rank=col[1]
				pval=col[7]
				#pvals.append(rank+':'+pval)
				pvals.append(pval)
			if 'numsnps used:' in line:
				numsnps=col[2]
			if '#' not in line and 'dscore' in line:
				dscores.append(col[1:])

		print target,'\t',','.join(sources),'\t',','.join(outgroups),'\t','\t'.join(pvals)
	else:
		for line in pileupline:
			col=line.split()
			if 'coefficients:' in line:
				props=col[2:]
			if 'std. errors:' in line:
				SEs=col[2:]
			if 'f4rank' in line:
				rank=col[1]
				pval=col[7]
				#pvals.append(rank+':'+pval)
				pvals.append(pval)
			if 'numsnps used:' in line:
				numsnps=col[2]
			if '#' not in line and 'dscore' in line:
				dscores.append(col[1:])

		print target,'\t',','.join(sources),'\t',','.join(outgroups),'\t',pvals[0],'\t',','.join(props),'\t',','.join(SEs),'\t',numsnps,'\t',
	
		if len(sources)>1:
			base='Empirical_'+target
			fitted='Modelled_'+target
			Rbase=outgroups[0]
			ddict={}
			for d in dscores:
				right2=d[0]
				f4=d[2]
				z=float(d[4])
				#ddict[z]='f4('+base+','+fitted+';'+Rbase+','+right2+'),Z= '
				ddict[z]=right2
				if options.details:
						print 'f4('+base+','+fitted+';'+Rbase+','+right2+'),Z= ',z
			maxz=max(ddict.keys(), key=abs)
			print ddict[maxz],maxz
		else:
			print '\n',