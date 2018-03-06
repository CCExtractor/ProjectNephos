#!/bin/bash
#
# Post-processing of the digital signal mpegts and closed captioning file from HDHomeRun devices
#
# Calls check-mpg-single.sh and cc-extract-teletext.sh
#
# Written by FFS on 29 June 2007
#
# To do:
#
#       2011-02-07: Double check before declaring roma a failure (last stanza)
#
# Changelog:
#
#       2015-11-06 Customized for Portugal, renamed from check-cc-hdhr, add host alias
#       2015-01-25 Prefer master node on equal word count
#       2015-01-15 Add SEG_00 placeholder for files without captions -- mv .tmp to .t
#       2015-01-15 Removed cc-wrong-starttime -- no longer needed
#       2014-10-11 Add the option to not give a duration and to skip hoffman
#       2014-10-10 Add cc-wrong-starttime-capture
#       2014-06-09 Use $SCRATCH for ts
#       2014-04-16 Remove the ts file after final quality check
#       2014-04-12 Repair with dvbt-ts-repair
#       2014-03-22 Add VID expected and original picture size
#       2013-11-25 Add $HOST to $FIL.len
#       2013-10-15 Convert caption styles to commercial segment tags
#       2013-07-22 Forked from check-cc-file -- removed Project-X
#       2013-02-10 Use projectx -tots instead of -tom2p to preserve metadata
#       2012-12-08 Set the duration to the scheduled time if the probed time is unreasonable
#       2012-05-08 LBT and comments are now written to file by channel
#       2012-02-08 Run cc-extract if there is no closed captioning
#       2011-09-27 Add local broadcast time in the header
#       2011-09-17 Support the new projectx naming convention
#       2011-08-25 Also copy to second storage server and backup server
#       2011-07-03 New-style header with UTC timestamp
#       2011-02-15 Only print the modified sed line, using -n and /p
#       2011-01-08 Add a timeout if there is no twin text file
#       2010-12-12 Use ProjectX to repair the captured mpegts file
#       2010-11-30 Modify for Kai's cc scheme, copy file to Ralph
#       2010-11-24 Modified ffprobe line to handle recent version
#       2008-08-28 Switched to ffprobe, since it handles mpg too
#       2008-08-20 Add the video length tag to the header
#
# -----------------------------------------------------------------------------------

# Config, correct for UNav
SPOOLROOT="/home/redhen/var/temp_recordings/"
STORAGEROOT="/tv"
CONFIGFILE="/home/redhen/etc/redhen.config"
DO_REPAIR="0"
DO_MOVE="0"

# Location of dependencies, leave variable empty to use PATH
LOC_FFPROBE="/usr/bin/ffprobe"
LOC_DVBTTSREPAIR="/usr/local/bin/dvbt-ts-repair"
LOC_EXTRACTOR="/home/redhen/ucla-scripts/cc-extract-teletext"

function show_help
{
      echo -e "\n\tSyntax: `basename $0` <filename> [-dur <duration in seconds>] [-page <teletext page #>]"
      echo -e "\n\t        `basename $0` 2015-12-04_2000_PT_RTP-1_Telejornal.mpg -dur 1770 -page 885"
      echo -e "\n\tThe script repairs the mpg file and writes a temporary ts file."
      echo -e "\n\tIt transfers the text to storage if it is longer than that on the twin.\n"
}

function parse_args
{
        while [ "$1" != "" ]; do
                case "$1" in
                        "-h" | "--help" | "help" )
                                show_help
                                exit 0
                                ;;
                        "-dur" )
                                ARGDUR="$2"
                                shift
                                ;;
                        "-page" )
                                ARGPAGE="$2"
                                shift
                                ;;
                        *)
                                if [[ "$FIL" != "" ]] ; then
                                        echo "Too many parameters (don't know what to do with $1)"
                                        exit 1
                                fi
                                FIL=${1%.*}
                                ;;
                        esac
                shift
        done
}

parse_args "$@"
if [[ "$FIL" == "" ]] ; then
        echo -e "\nUsage: `basename $0` -h\n" ;
        exit 1
fi

# OSX customizations (use GNU Core Utilities from MacPorts coreutils)
if [ "$(uname)" = "Darwin" ]
  then DAT="gdate" SED="gsed" STAT="gstat" SEQ="gseq" MV="gmv" CP="gcp"
  else DAT="date"  SED="sed"  STAT="stat"  SEQ="seq"  MV="mv" CP="cp"
fi

# If the parameter contains a slash (/) then we're given a full path,
# otherwise use the standard RedHen organization structure
if [[ $FIL == */* ]] ; then
        FFIL=$FIL
else
        FFIL=${SPOOLROOT}/${FIL:0:4}/${FIL:0:7}/${FIL:0:10}/$FIL
fi

# A. Assign variables

# Video duration variables
# ScheDUR is the length in seconds of the recording given in the schedule -- the target length
# ffDUR is the length in hours, minutes, seconds, and milliseconds of the video, found through ffprobe
# ffDURs is the same value in seconds and ffDURm the same value in minutes
# DUR is the value that gets written in the DUR field in the header -- it's not always a number, but typically ffDUR

# Use or set the last timestamp (set by channel)
if [ -f $FFIL.txt ] ; then END="$( grep '^END|' $FFIL.txt )" ; fi
if [ "END" = "" ] ; then END="END|$($DAT -u '+%Y%m%d%H%M%S')|$FIL" ; fi

# Scheduled duration
if [ -z "$ARGDUR" ] ; then ScheDUR=0 ; echo -e "\n\tWarning: No recording duration given\n" ; sleep 10 ; else ScheDUR="$ARGDUR" ; fi

# Teletext page
if [ -z "$ARGPAGE" ] ; then TTP=$ARGPAGE ; fi

# Host
HOST="$( hostname -s )"

# Working directory
WDIR="$HOME/ts/logs" ; mkdir -p $WDIR

# Define the recipients of failure messages
TO="$( grep e-mail $CONFIGFILE | cut -d"=" -f2 )" ; if [ -z "$TO" ] ; then echo -e "\n\tNot finding the e-mail recipient -- please fix.\n" ; exit 1; fi

# Define the alert file name
ALERT="$WDIR/$($DAT '+%F_%H%M')_E-mail-alert"

# Here you really should look at the schedule to see if the file completed --
# and use the scheduled value to determine $ScheDUR and whether to send an
# e-mail warning that the recording likely failed and should be rescheduled

# Define the trouble log
FAILED="$WDIR/$(date +%F)-`basename $0`-failure"

# Pull out the date components of the file
t=`echo "$FIL" | $SED -r 's/.*([0-9]{4})-([0-9]{2})-([0-9]{2}).*/YEAR=\1 MONTH=\2 DAY=\3/'`
if [[ "$t" != YEAR*MONTH*DAY* ]] ; then
        echo "File name cannot be parsed to extract year, month and day"
        exit
fi
eval $t
# Set the storage directory
if [[ "$DO_MOVE" == "1" ]] ; then
        DDIR="$STORAGEROOT/$YEAR/$YEAR-$MONTH/$YEAR-$MONTH-$DAY"
else
        # Work directly in the spool
        DDIR="$SPOOLROOT"
fi

# Verify the captured file exists
if [ -f ${SPOOLROOT}/${FIL}.mpg  ] ; then EXT=mpg
  else EXT=none DUR="Video missing"
fi

if [[ "$DO_REPAIR" == "1" ]] ; then
        # Repair with dvbt-ts before extracting the text
        echo -e "`date +%F\ %H:%M` \t${HOST:0:4} \tdvbt-ts-repair \t$FIL.mpg" | tee -a $LLOG
        ${LOC_DVBTTSREPAIR} /mnt/spool/$FIL.mpg $DDIR/$FIL.ts

        # Or with project-x (this takes a few minutes -- wants X.ini in $HOME)
        #if [ ! -f $DDIR/$FIL.ts ]
        #  then echo -e "`date +%F\ %H:%M` \t${HOST:0:4} \tproject-x \t$FIL.mpg" | tee -a $LLOG
        #  projectx -tots $DIR/$FIL.mpg -out $DDIR -name $FIL.ts 2>&1 > /dev/null
        #  if [ -f $DDIR/$FIL[remux].ts ] ; then mv -n $DDIR/$FIL[remux].ts $DDIR/$FIL.ts ; fi
        #fi
fi

# Use the ts file if present
if [ -f $DDIR/$FIL.ts ] ; then EXT=ts ; fi

cd $DDIR

# Move to the tv directory
if [[ "$DO_MOVE" == "1" ]] ; then
        mv ${SPOOLROOT}/$FIL.mpg $DDIR 2>/dev/null
fi

# B. Complete the header

# Get the video length (could be corrected by the mp4 length later)
# Only print the modified line (see http://www.grymoire.com/Unix/Sed.html#uh-9)
ffDUR="$($LOC_FFPROBE $DDIR/$FIL.$EXT 2>&1 | grep Duration | $SED -rn s/'.*([0-9]{1}:[0-9]{1,2}:[0-9]{1,2}\.[0-9]{2,3}).*/\1/p' )"

# Second chance
if [ "$ffDUR" = "" ] ; then
  ffDUR="$($LOC_FFPROBE ${SPOOLROOT}/$FIL.mpg 2>&1 | grep Duration | $SED -rn s/'.*([0-9]{1}:[0-9]{1,2}:[0-9]{1,2}\.[0-9]{2,3}).*/\1/p' )"
fi

# Set the duration to the scheduled time if the probed time is unreasonable
ffDURs="$( $DAT -ud 1970-01-01\ $ffDUR +%s 2>/dev/null )"
if [[ "$( echo "$ffDURs" | grep '[^0-9]' )" = "" && "$ffDURs" != "" && "$ScheDUR" != "0" ]] ; then DiffDUR=$[ $ffDURs - $ScheDUR ]
  if [ "$DiffDUR" -gt 1000 -o "$DiffDUR" -lt -1000 ]
    then DUR="$( $DAT -ud "+$ScheDUR seconds"\ $($DAT +%F) +%H:%M:%S )"
    else DUR="$( $DAT -ud "+$ffDURs seconds"\ $($DAT +%F) +%H:%M:%S )"
  fi
fi

# If the scheduled time is missing, set it to the probed time (useful for manual runs)
if [ "$ScheDUR" = "0" ] ; then ScheDUR=$ffDURs ; fi

# Get the original picture size from ts
if [ -z "$PIC" ]
  then PIC="$( $LOC_FFPROBE $DDIR/$FIL.$EXT 2>&1 | grep Stream | grep Video | head -n1 | $SED -r 's/.*\ ([0-9]{3,4}x[0-9]{3,4})[\ ,]{1}.*/\1/' )"
    if [ ${#PIC} -gt 9 ] ; then PIC="Video damaged" ; fi
fi

# Get the original picture size from mpg
if [ -z "$PIC" ]
  then PIC="$( $LOC_FFPROBE $DDIR/$FIL.mpg 2>&1 | grep Stream | grep Video | head -n1 | $SED -r 's/.*\ ([0-9]{3,4}x[0-9]{3,4})[\ ,]{1}.*/\1/' )"
    if [ ${#PIC} -gt 9 ] ; then PIC="Video damaged" ; fi
fi

# The video will be scaled during compression (one-offs include 1220x720 1164x720 1440x1080)
case "$PIC" in
  1920x1088) VID="640x352" ;;
  1920x1080) VID="640x352" ;;
  1280x720 ) VID="640x352" ;;
   720x576 ) VID="640x512" ;;
   720x480 ) VID="640x426" ;;
     *) VID="$PIC" ;;
esac

# Makeshift
#if [ -f $FIL.tmp ] ; then mv $FIL.tmp $FIL.t ; fi

# Add the collection name, an identifier, and the video duration (insert after the first line, TOP)
if [ "$( grep ^'DUR|' $FIL.txt | cut -d"|" -f2 )" = "" ] ; then
  $SED -i "1a`echo "COL|Communication Studies Archive, UCLA\nUID|$(uuid -v1)\nDUR|"$DUR"\nVID|"$VID"|"$PIC""`" $DDIR/$FIL.txt
fi

# C. Text extraction
# Get the closed captioning
echo ${LOC_EXTRACTOR} ${DDIR}/${FIL} $TTP
${LOC_EXTRACTOR} ${FIL} $TTP

# Debug on
#set -x

# In case cc-extract-teletext fails
#if [ ! -s $FIL.txt ] ; then mv $FIL.tmp $FIL.txt ; fi

# Verify presence
if [ ! -f $FIL.txt ] ; then echo -e "\n\tNot finding $FIL.txt\n" ; exit ; fi

# Verify END
if [ "$( grep -a '^END|' $FIL.txt )" = "" ] ; then echo "$END" >> $FIL.txt ; fi

# Verify placeholder SEG
if [ ! "$( egrep -a -m1 '^1|^2' $FIL.txt )" ] ; then
  SEG="$( grep -a '^TOP|' $FIL.txt | cut -d"|" -f2 ).000|$( grep -a '^END|' $FIL.txt | cut -d"|" -f2 ).000|SEG_00|Type=Placeholder"
  $SED -i "/^END|/i $SEG" $FIL.txt
fi

# Convert caption styles to commercial segment tags (US only)
#cc-tag-commercials $FIL.txt

# D. Word count

# Strip the header and timestamps
cat $FIL.txt | cut -d"|" -f4-9 > $FIL.wc1

# Remove XDS lines
$SED -i '/XDS/d' $FIL.wc1

# Show me the file (verify only words left)
#cat $FIL.wc1

# Count remaining words
CCWORDS="$(cat $FIL.wc1 | wc -w | xargs)"

# Convert seconds to minutes
ffDURm=$[$ffDURs/60]
if [ "$ffDURm" = "0" ] ; then ffDURm=1 ; fi

# Calculate rate
CCRATE=$[$CCWORDS/$ffDURm]

# Display rate
echo -e "\t${HOST^} captured $CCWORDS words ($CCRATE/min)"

# Save the count to file
echo $CCWORDS > $FIL.wc

# Durations in seconds -- recording time, resultant file, word count
if [ "$ffDUR" = "" ] ; then ffDUR=0 ; fi
ffDURs=$( $DAT -u -d 1970-01-01\ $ffDUR +%s )
TIMDIFF="$( echo "scale = 3; $ScheDUR - $ffDURs" | bc )"
if [ "$CCWORDS2" = "" ] ; then CCWORDS2=0 ; fi
CCDIFF="$( echo "scale = 3; $CCWORDS2 - $CCWORDS" | bc )"
echo -e "unav \t$CCWORDS \t$CCWORDS2 \t$CCDIFF \t$ScheDUR \t$ffDURs \t$TIMDIFF \t$FIL.$EXT" > $FIL.len

# Get the video quality measures
check-mpg-single.sh $FIL

# Remove the ts file (we could keep it and remove the mpg file instead -- keeping both takes too much space)
rm -f $DDIR/${FIL%.*}.ts

# Clean up
rm -f $FIL.wc* $LLOG

# EOF

