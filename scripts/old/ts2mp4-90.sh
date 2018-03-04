#!/bin/bash
#
# ~/bin/ts2mp4.sh
#
# Convert incoming mpeg files to mp4
#
# Called by ~/bin/node-daemon.sh
#
# Written 2012-12-20 FFS
#
# Document in http://vrnewsscape.ucla.edu/cm/Hoffman2
#
# Changelog:
#
#	2017-03-12 For BE, use language rather than country (should be generalized)
#	2016-09-17 Complete processing for _CZ_ and _PL_ files (provisional)
#	2016-05-21 Allow up to 500 seconds more or less -- the second file is rarely an improvement
#	2016-03-11 Keep the mp4 file -- could be useful for frame extraction
#	2016-02-12 Complete processing for _BR_ and _PT_ files (provisional)
#	2016-01-18 Check the first rather than the second audio track for length
#       2015-12-17 Improve video duration detection
#	2015-11-26 Ffmpeg's scale filter is still not working; add support for European ts files
#	2015-09-17 Try handbrake if ffmpeg fails, and also reject videos that are too long
#	2014-12-03 Try ffmpeg first -- handbrake can give rise to purple frames (should be reported)
#	2014-10-17 Keep the handbrake log for detecting broken video better handled by ffmpeg
#	2014-05-07 Allow mov for mp4 to mp4 conversions (rename mp4 to mov manually first)
#	2014-05-29 Try hoffman2.idre.ucla.edu first
#	2014-04-18 Strongly prefer ts
#	2014-01-25 Include ~/tv/pool as potential location for half-processed files (from an interrupted process)
#	2014-01-24 Use $SCRATCH for drops ($HOME fills up too fast)
#	2013-12-03 Use $HOME/tv2 instead of $SCRATCH; and $HOST to logs
#	2013-12-03 Copy the completed file to storage right away
#	2013-11-25 Add parameter for scratch directory to use local drive
#	2013-11-04 Silence the locks
#	2013-11-03 Revert to earlier version of cpulimit -- new version crashes
#	2013-10-30 New version of cpulimit, called cpulimit2 for now
#	2013-09-14 Add silent lock in HOME -- the POOL lock sometimes fails
#	2013-03-31 Fork from mpg2h264-5.sh, deleting everything except mp4 conversion
#	2013-03-07 Do not time out handbrake if the mp4 file has been created and is recent
#	2013-01-13 Add fallback option for audio stream order for a second run
#	2013-01-11 Detailed audio stream logic to track movement by projectx -tots; add $HBMAP
#	2013-02-03 Fixed LD_LIBRARY_PATH and switched ffmpeg to fdk_aac for 96k bitrate support
#	2013-01-29 Switch to locally built ffmpeg, with aac+ and x264 support
#	2013-01-28 Add max drop user variable
#	2013-01-24 Add second audio track with FFmpeg $FFMAP
#	2013-01-18 Add second audio track with Handbrake -a 1,2
#	2013-01-17 Try ffmpeg if handbrake fails
#	2013-01-09 Added a soft kill for handbrake -- retry once under three conditions
#	2013-01-06 Use `basename $0` to permit switching between versions
#	2013-01-04 Retry handbrake on segmentation fault
#	2012-12-31 Process only the file specified
#	2012-12-30 Background handbrake and check PID for stalls
#
# Todo:
#
#	2012-12-23 better logging
#
# WARNING: Any changes you make to this script will affect currently running processes!
# Maintain a succession of numbered versions, ts2mp4-00.sh to 99, and activate the last one
# using echo ts2mp4-25.sh > ts2mp4.name -- used by node-daemon-local.sh.
#
# ------------------------------------------------------------------------------------------

# Home directory
HOME=/u/home/f/fsteen

# Scratch directory
#SCRATCH=/u/scratch/f/fsteen
SCRATCH=$HOME/tv2

# Script name
SCRIPT=`basename $0`

# Dereference script name when called manually
SCRIPT="$( readlink -f $HOME/bin/$SCRIPT )" SCRIPT=${SCRIPT##*/}

# Help screen
if [ "$1" = "-h" -o "$1" = "--help" -o "$1" = "help" ]
 then echo -e "\n$SCRIPT"
  echo -e "\n\tThe ts2mp4 script converts an mpeg2 file to mp4\n"
  echo -e "\tSyntax:\n"
  echo -e "\t\t$SCRIPT <filename.ext> [<max drop>] [<threads>] [local]\n"
  echo -e "\tAccept up to maximum number of seconds dropped, default 10."
  echo -e "\tDefault threads is auto, legal values 1-8."
  echo -e "\tOptionally set scratch to the local drive on a compute node.\n"
  echo -e "\tDefault video bitrate is 450 kbps"
  echo -e "\tDefault audio bitrate is 96 kbps (constant bitrate)"
  echo -e "\tDefault size is width 640, maintain aspect"
  echo -e "\tDefault framerate is 29.97 (NTSC)"
  echo -e "\tDefault threads is auto\n"
  echo -e "\tCalled by node-daemon.sh, ocr-daemon-local.sh, and node-daemon-local.sh.\n"
  echo -e "\tThe completed file is copied to storage.\n"
  echo -e "\tThe script is designed to run on the hoffman2 cluster.\n"
   exit
fi

# Start time
START=$( date +%s )

# Binaries
LBIN=$HOME/bin

# Primary reservations
RDIR=$SCRATCH/pool

# Shared OCR tree
OCR=$SCRATCH/ocr

# Log directory
LOGS=$SCRATCH/logs

# Shared or local processing
if [ -z "$4" ]

  # Shared processing
  then SDIR=$SCRATCH/pool

    # Backup reservations
    R2DIR=$HOME/reservations

  # Local processing -- local source but shared scratch
  else SDIR=/work/pool ; mkdir -p $SDIR

    # Alternative pool (from interrupted jobs)
    S2DIR=/u/scratch/f/fsteen/pool

    # Backup reservations
    R2DIR=$SDIR

fi

# Get the file name
if [ -z "$1" ] ; then echo -e "\n\tPlease give a file name to process (with extension)\n" ; exit ; else FIL=$1 ; fi

# Short forms
FIL="${1##*/}" EXT="${FIL##*.}"  FIL="${FIL%.*}"  SFIL=$SDIR/$FIL

# Prefer ts, then mpg, then mov (for mp4 to mp4 conversions)
if [ -f $SDIR/$FIL.ts ] ; then EXT=ts
  elif [ -f $SDIR/$FIL.mpg ] ; then EXT=mpg
  elif [ -f $SDIR/$FIL.mov ] ; then EXT=mov
  else echo -e "\n\tUnable to locate the file $FIL\n" ; exit
fi

# Copy the files from the scratch spool if present -- used for interrupted jobs
#if [ ! -f $SDIR/$FIL.mpg ] ; then if [ -f $S2DIR/$FIL.mpg ] ; then mv $S2DIR/$FIL.* $SDIR/ ; fi ; fi

# Verify the file exists
if [ ! -s $SFIL.$EXT ] ; then echo -e "\n\tNot finding a file called $1 in the pool\n" ; exit ; fi

# Tolerate up to max number of seconds dropped
if [ -z "$2" ]
  then MAXDROP=500
  else MAXDROP=$2
fi

# Optional limit on the number of cores
if [ -z "$3" ]
  then THREADS="400"
  else THREADS="$3"00
fi

# Use the .name content if present
if [ -f $HOME/bin/${SCRIPT%.*}.name ] ; then SCRIPT="$( cat $HOME/bin/${SCRIPT%.*}.name )" ; fi

# Check that the script exists
if [ ! -f $HOME/bin/$SCRIPT ] ; then echo -e "\nUnable to find the script $HOME/bin/$SCRIPT.\n" ; exit ; fi

# Script name as shown in myjobs (partial match is fine)
SCRIPJ=${SCRIPT:0:6}

# Host
HOST="$( hostname -s )"

# Wait until the ts file is ready
while true ; do

  # Get the age of the file with the given extension  -- for some reason this command occasionally fails, so persist
  AGE=0 ; while [ "$AGE" -eq 0 ] ; do AGE="$( date -r $SFIL.$EXT +%s )" ; done ; NOW="$(date +%s)" ; DIFF=$[NOW-AGE]

  # Skip files that were updated less than x seconds ago -- they may still be forming
  if [ "$DIFF" -lt "57" ] ; then echo -e "\n\t$FIL.$EXT is less than sixty seconds old\n" ; sleep 10 ; else break ; fi

done

# Skip if the .ts file is not ready -- unless this is a mov conversion
#if [ ! -f ${SFIL%.*}.ts -a ! -f ${SFIL%.*}.mov ] ; then echo -e "\n\tNot finding $FIL.ts in the pool\n" ; exit ; fi

# Generate tree
DDIR="$(echo $FIL | sed -r 's/([0-9]{4})-([0-9]{2})-([0-9]{2}).*/\1\/\1-\2\/\1-\2-\3/')"
mkdir -p $OCR/$DDIR

# Skip if the file is marked done
if [[ -d $RDIR/$FIL.mp4.done || -d $OCR/$DDIR/$FIL.mp4.done || -d $R2DIR/$FIL.mp4.done ]] ; then echo -e "\n\tMarked as done -- $FIL.mp4.done\n" ; exit ; fi

# Convert the age of the $EXT file to hours, minutes, and seconds for the log
AGE=0 ; while [ "$AGE" -eq 0 ] ; do AGE="$( date -r $SFIL.$EXT +%s )" ; done ; NOW="$(date +%s)" ; DIFF=$[NOW-AGE]
DIFF="$(date -ud "+$DIFF seconds"\ $(date +%F) +%H:%M:%S)"

# Holding pen for mp4 files with dropped video (partially failed conversions)
#DROPS=$SCRATCH/drops
DROPS=/u/scratch/f/fsteen/drops

# Create the directory if needed
mkdir -p $DROPS

# Log directory
LOGS=$SCRATCH/logs

myjobs | grep $HOST | tail -n 1 | cut -d" " -f1

# Get the current grid engine queue number
QNUM="$( echo $PATH | sed -r 's/.*\/work\/([0-9]{3,7})\..*/\1/' )"

# On exclusive nodes, use the process list
if ! [[ "$QNUM" =~ ^[0-9]+$ ]] ; then QNUM="$( ps x | grep job_scripts | grep -v grep | tail -n 1 | sed -r 's/.*\/([0-9]{2,8})/\1/' )" ; fi

# On interactive nodes, infer the queue number from the node name
if ! [[ "$QNUM" =~ ^[0-9]+$ ]] ; then QNUM="$( myjobs | grep $HOST | tail -n 1 | cut -d" " -f1 )" ; fi

# If the queue number is not found, use zero -- or just exit? Normally this means you don't have rights.
if ! [[ "$QNUM" =~ ^[0-9]+$ ]] ; then QNUM=0000000 ; echo -e "\n\tCannot find a queue number\n" ; fi #exit ; fi

# Get the components of the file name
eval $( echo "$FIL" | sed -r 's/[0-9_-]{15}_([A-Z]{2})_([A-Za-z0-9-]{2,20})_(.*)/COUNTRY=\1 NWK=\2 SHOW=\3/' )

# Log file stem
STEM=${FIL:0:19}$NWK

# Derive the log file name
QLOG=$LOGS/$SCRIPT-$STEM.$QNUM

# Add libraries for local ffmpeg (ffprobe)
export LD_LIBRARY_PATH+=:$HOME/lib/

# Debug
#echo -e "\n\tLD_LIBRARY_PATH line 106 is $LD_LIBRARY_PATH\n"

# Set the reservations log
LLOG=$LOGS/reservations.$( date +%F ) ; touch $LLOG

# Make sure you have a .txt file -- you have to go via a login node (should never trigger)
TXT=$OCR/$DDIR/$FIL.txt ; if [ -f $SFIL.txt ] ; then TXT=$SFIL.txt ; elif [ -f /work/ocr/$DDIR/$FIL.txt ] ; then TXT=/work/ocr/$DDIR/$FIL.txt ; fi

if [ ! -s $TXT ] ; then ssh hoffman2.idre.ucla.edu "rsync tna@164.67.183.179:/sweep/./$DDIR/$FIL.txt $OCR/ -aR" && sleep 10 ; fi

n=0 ; while [ "$n" -lt "6" ] ; do n=$[n+1]
   if [ -s $TXT ] ; then break ; else ssh login$n "rsync tna@164.67.183.179:/sweep/./$DDIR/$FIL.txt $OCR/ -aR" && sleep 10 ; fi
  #if [ -s $TXT ] ; then break ; else ssh hoffman2.idre.ucla.edu "rsync tna@164.67.183.179:/tv/./$DDIR/$FIL.txt $OCR/ -aR" && sleep 10 ; fi
done

# Get the show duration from the .txt or the .txt2 file
if [ -z "$LEN" ] ; then
  DUR="$( grep -a '^DUR|' $TXT "$TXT"2 | head -n1 | cut -d"|" -f2 )"
  LEN="$(date -ud 1970-01-01\ $DUR +%s)"
fi

# If this still fails, exit -- several operations below depend on a good length value
if [ -z "$LEN" -o "$LEN" = "0" ]
  then echo -e "`date +%F\ %H:%M:%S` \t${SCRIPT%.*} \t$QNUM\t$HOST \tFailing \tNo length \t$FIL.$EXT" | tee -a $LOGS/reservations.$( date +%F ) ; exit
fi

# Get language new style
LAN=$( grep ^CC1 $TXT | sed -r 's/CC1\|([A-Z]{3}).*/\1/' )

# Old style language
if [[ $LAN =~ ^[A-Z]{3}$ ]] ; then echo -n ; else LAN=$( grep ^LAN $TXT | sed -r 's/LAN\|([A-Z]{3}).*/\1/' ) ; fi

# Verify
if [[ $LAN =~ ^[A-Z]{3}$ ]] ; then echo -n ; else LAN="" ; fi

# Check the file is non-zero (may just be being sync'ed to roma and deleted)
if [ ! -s $SFIL.$EXT ] ; then echo -e "\n\t$FIL.$EXT is an empty file\n" ; exit ; fi

# Attempt to reserve the file
if [ "$( mkdir $RDIR/$FIL.compressed 2> /dev/null; echo $? )" = "0" ]
  then echo -e "`date +%F\ %H:%M:%S` \t${SCRIPT%.*} \t$QNUM\t$HOST \t$DUR \t$FIL.$EXT" > $RDIR/$FIL.compressed/$QNUM
    echo -e "`date +%F\ %H:%M:%S` \t${SCRIPT%.*} \t$QNUM\t$HOST \tCompress \t$DIFF \t$FIL" | tee -a $LOGS/reservations.$( date +%F )
  else echo -e "\n\t$FIL is already reserved for compression\n" ; exit
fi

# Secondary reservation (not needed?)
if [ "$( mkdir $R2DIR/$FIL.compressed 2> /dev/null; echo $? )" = "0" ]
  then echo -e "`date +%F\ %H:%M:%S` \t${SCRIPT%.*} \t$QNUM\t$HOST \t$DUR \t$FIL.$EXT" > $R2DIR/$FIL.compressed/$QNUM
    #echo -e "`date +%F\ %H:%M:%S` \t${SCRIPT%.*} \t$QNUM\t$HOST \tLoc lock \t$DIFF \t$FIL" | tee -a $LOGS/reservations.$( date +%F )
  else echo -e "\n\t$FIL is already reserved for compression -- $R2DIR reservation failed!\n" | tee -a $LOGS/reservations.$( date +%F ) ; exit
fi

# Check the file is still non-zero (may just have been sync'ed to roma and deleted)
if [ ! -s $SFIL.$EXT ] ; then echo -e "\n\t$FIL is an empty file\n" ; exit ; fi

# Welcome
echo -e "\n\tStarting $SCRIPT on $HOST at $(date +%Y-%m-%d\ %H:%M:%S) for $FIL.$EXT\n"

# Fallback audio track ordering (for a second run when the projectx log is gone -- or maybe you just keep the projectx log?)
if [ "$HBMAP" = "" ] ; then

  # Map audio tracks -- projectx moves them around, but most files are now repaired with dvb-ts
  TRACKS=1

  # How many audio tracks? (It is possibly risky to use the .ts file for this, as it may give an extra spurious track)
  if [ -f "$SFIL.$EXT" ] ; then TRACKS="$( $HOME/bin/ffprobe $SFIL.$EXT 2>&1 | grep Stream | grep Audio | wc -l )" ; fi

  # Map audio tracks if there is more than one
  if [ "$TRACKS" -gt 1 ] ; then

    # European files may have teletext as stream 0:0 -- find out if ffmpeg supports zvbi teletext encoding
    if [ "$( $HOME/bin/ffprobe $SFIL.$EXT 2>&1 | grep 'Stream #0:0' | grep dvb_teletext )" ]
      then FFMAP="-map 0:1 -map 0:2" HBMAP="-a 1"

     # UNav files have teletext as stream 0:1
     elif [ "$( $HOME/bin/ffprobe $SFIL.$EXT 2>&1 | grep 'Stream #0:1' | grep dvb_teletext )" ]
      then FFMAP="-map 0:0 -map 0:2" HBMAP="-a 2"

     # Brazilian Globo files need explicit mapping of audio to 0:1, it doesn't hurt the other Brazilian files
     elif [[ "$COUNTRY" = "BR" ]] # && "$NWK" = "Globo" ]]
      then FFMAP="-map 0:0 -map 0:1" HBMAP="-a 1"

     # Many European files don't need any explicit mapping -- ffmpeg figures it out -- fixme: you should put this in a parameter file, use language not country?
     elif [[ "$LAN" = "NLD" || "$COUNTRY" = "CZ" || "$COUNTRY" = "DE" || "$COUNTRY" = "FR" || "$COUNTRY" = "IT" || "$COUNTRY" = "PL" || "$COUNTRY" = "PT" ]] ; then FFMAP="" HBMAP=""

      # Put the track bitrates into an array
      else AKBS=($( $HOME/bin/ffprobe $SFIL.$EXT 2>&1 | grep Stream | grep Audio | sed -r 's/.*fltp,\ ([0-9]{2,4})\ kb.*/\1/' ))

        # Compare the first two values and assume the larger is the main language, in this case labeled ENG (but the label does not matter)
        if [ ${AKBS[0]} -gt ${AKBS[1]} ] ; then ENG=1 SPA=2 ; else ENG=2 SPA=1 ; fi

        # Mapping string for ffmpeg conversion
        FFMAP="-map 0:0 -map 0:$ENG -map 0:$SPA"

        # Mapping string for handbrake conversion
        HBMAP="-a $ENG,$SPA"
    fi

  fi

fi

# Try ffmpeg first
if [ ! -s $SFIL.mp4 ] ; then

  # Reset library path for local ffmpeg only (likely not required)
  export LD_LIBRARY_PATH=$HOME/lib/

  # Debug
  #echo -e "\n\tLD_LIBRARY_PATH line 387 is $LD_LIBRARY_PATH\n"

  # Create a working directory to avoid overwriting the log (not needed?)
  mkdir /tmp/ffmpeg-$$ ; cd /tmp/ffmpeg-$$

  # Frame size
  SIZ="$( $HOME/bin/ffprobe $SFIL.$EXT 2>&1 | grep Stream | grep Video | sed -r 's/.*\ ([0-9]{3,4}x[0-9]{3,4})\ .*/\1/' )"

  # Add metadata
  # -metadata author="$NETWORK" -metadata title="$SHOW"

  echo -e "`date +%F\ %H:%M:%S` \t${SCRIPT%.*} \t$QNUM\t$HOST \tFfmpeg    \tCompress $LEN \t$FIL.$EXT" | tee -a $LOGS/reservations.$( date +%F )

  # FIXME: the ffmpeg conversion should be backgrounded for hang monitoring, like handbrake below

  if [ "$HOST" = "n6288" -o "$HOST" = "n7288" ]

    then

      # Scale the video appropriately (divisible by 4) with the scale filter
      # -acodec libaacplus handles only 32k and 64k -- and is likely the best option for 64k
      # Use the same audio encoding for both passes to avoid Incomplete MB-tree stats file
      # See http://ubuntuforums.org/showpost.php?p=12421935&postcount=34 for encoding suggestions using variable bitrate
      #$HOME/bin/cpulimit1 -l $THREADS $HOME/bin/ffmpeg -i $SFIL.$EXT -pass 1 -y $FFMAP -vcodec libx264 -r 29.97 -b:v 450k -threads 0 -vf scale="640:-1" -acodec libfdk_aac -b:a 96k -ac 2 -ar 44100 -f mp4 /dev/null &> /dev/null
      #$HOME/bin/cpulimit1 -l $THREADS $HOME/bin/ffmpeg -i $SFIL.$EXT -pass 2 -y $FFMAP -vcodec libx264 -r 29.97 -b:v 450k -threads 0 -vf scale="640:-1" -acodec libfdk_aac -b:a 96k -ac 2 -ar 44100 $SFIL.mp4 &> /dev/null
      $HOME/bin/ffmpeg -analyzeduration 2G -probesize 2G -i $SFIL.$EXT -pass 1 -y $FFMAP -vcodec libx264 -r 29.97 -b:v 450k -threads 0 -vf scale="640:trunc(ow/a/2)*2" -acodec libfdk_aac -b:a 96k -ac 2 -ar 44100 -f mp4 /dev/null &> /dev/null
      $HOME/bin/ffmpeg -analyzeduration 2G -probesize 2G -i $SFIL.$EXT -pass 2 -y $FFMAP -vcodec libx264 -r 29.97 -b:v 450k -threads 0 -vf scale="640:trunc(ow/a/2)*2" -acodec libfdk_aac -b:a 96k -ac 2 -ar 44100 $SFIL.mp4 &> /dev/null

    else

      $HOME/bin/cpulimit1 -l $THREADS $HOME/bin/ffmpeg -analyzeduration 2G -probesize 2G -i $SFIL.$EXT -pass 1 -y $FFMAP -vcodec libx264 -r 29.97 -b:v 450k -threads 0 -vf scale="640:trunc(ow/a/2)*2" -acodec libfdk_aac -b:a 96k -ac 2 -ar 44100 -f mp4 /dev/null &> /dev/null
      $HOME/bin/cpulimit1 -l $THREADS $HOME/bin/ffmpeg -analyzeduration 2G -probesize 2G -i $SFIL.$EXT -pass 2 -y $FFMAP -vcodec libx264 -r 29.97 -b:v 450k -threads 0 -vf scale="640:trunc(ow/a/2)*2" -acodec libfdk_aac -b:a 96k -ac 2 -ar 44100 $SFIL.mp4 &> /dev/null

  fi

  # Verify that the conversion was successful -- first get the length of the video and audio
  AUDLEN="$( $HOME/bin/mp4info $SFIL.mp4 2>/dev/null | grep -m1 audio | sed -r s/'.*\ ([0-9]{1,5}\.[0-9]{1,4})\ secs.*/\1/' | cut -d" " -f1 )"
  VIDLEN="$( $HOME/bin/mp4info $SFIL.mp4 2>/dev/null | grep video | sed -r s/'.*\ ([0-9]{1,5}\.[0-9]{1,4})\ secs.*/\1/' )"

  # If the mp4 conversion failed to produce a readable file
  if [ "$VIDLEN" = "" ] ; then VIDLEN=0 AUDLEN=0 ; fi

  # Or if the bitrate is zero (you could check that the bitrate is correct)
  if [ "$( $HOME/bin/mp4info $SFIL.mp4 2>/dev/null | grep -m1 audio | grep ' 0 kbps' )" ] ; then AUDLEN=0 ; fi

  # Compare the video and audio durations with the original show -- add a leading zero if needed
  DIFFVID="$( echo "$VIDLEN - $LEN" | bc | sed -r 's/^(-?)\./\10\./' )"
  DIFFAUD="$( echo "$AUDLEN - $LEN" | bc | sed -r 's/^(-?)\./\10\./' )"

  # Allow $MAXDROP seconds of slack in video and audio length, and mark & set aside or remove videos that are too long or too short
  if [[ ( "${DIFFVID%.*}" -lt 0 && "$( echo "$DIFFVID < -$MAXDROP" | bc )" = 1 ) || ( "${DIFFAUD%.*}" -lt 0 && "$( echo "$DIFFAUD < -$MAXDROP" | bc )" = 1 ) ]]
    then echo -e "`date +%F\ %H:%M:%S` \t${SCRIPT%.*} \t$QNUM\t$HOST \tFfmpeg    \tDROP "$DIFFVID"s \t$FIL.mp4" | tee -a $LOGS/reservations.$( date +%F )
      if [[ -s $SFIL.mp4 && ( "${DIFFVID%.*}" -gt -500 || "${DIFFAUD%.*}" -gt -500 ) ]] ; then mv $SFIL.mp4 $DROPS/$FIL-VDROP$DIFFVID-ADROP$DIFFAUD.mp4 ; else rm -r $SFIL.mp4 ; fi
    elif [[ ( "${DIFFVID%.*}" -gt 0 && "$( echo "$DIFFVID > $MAXDROP" | bc )" = "1" ) || ( "${DIFFAUD%.*}" -gt 0 && "$( echo "$DIFFAUD > $MAXDROP" | bc )" = "1" ) ]]
     then echo -e "`date +%F\ %H:%M:%S` \t${SCRIPT%.*} \t$QNUM\t$HOST \tFfmpeg    \tADDS "$DIFFVID"s \t$FIL.mp4" | tee -a $LOGS/reservations.$( date +%F )
      if [[ -s $SFIL.mp4 && ( "${DIFFVID%.*}" -lt 500 ) || ( "${DIFFAUD%.*}" -lt 500 ) ]] ; then mv $SFIL.mp4 $DROPS/$FIL-VADDS$DIFFVID-AADDS$DIFFAUD.mp4 ; else rm -r $SFIL.mp4 ; fi
    else echo -e "`date +%F\ %H:%M:%S` \t${SCRIPT%.*} \t$QNUM\t$HOST \tFfmpeg    \tEnd "$DIFFVID"s \t$FIL.mp4" | tee -a $LOGS/reservations.$( date +%F )
  fi

fi  # End of ffmpeg compression

# If the ffmpeg ts to mp4 conversion failed, convert ts to mp4 with handbrake-- background the process to allow hang monitoring
#if [ ! -s $SFIL.mp4 ] ; then LOOP=3

# Handbrake is not currently working
if false ; then LOOP=3
  echo -e "`date +%F\ %H:%M:%S` \t${SCRIPT%.*} \t$QNUM\t$HOST \tHandBrake  \tBegin $LEN \t$FIL.$EXT" | tee -a $LOGS/reservations.$( date +%F )

  # Reset library path for local ffmpeg only
  export LD_LIBRARY_PATH=$HOME/lib/

  # Load module support and handbrake module
  . /u/local/Modules/default/init/modules.sh
  module load handbrake

  # Debug
  #echo -e "\n\tLD_LIBRARY_PATH line 327 is $LD_LIBRARY_PATH\n"

  # Define the core command -- Was a cpulimit given?
  if [ "$THREADS" = "" ]
    then HandBrakeCLI="HandBrakeCLI"
    else HandBrakeCLI="$HOME/bin/cpulimit1 -l $THREADS HandBrakeCLI"
  fi

  while [ $LOOP -gt 0 ] ; do LOOP=$[LOOP-1]
    #$HandBrakeCLI -i $SFIL.$EXT -o $SFIL.mp4 -e x264 -2 -T -r 29.97 -b 450 $HBMAP -E faac -B 96 -R 44.1 -D 2 -w 640 -d slower --crop 0:0:0:0 -x ref=3:mixed-refs:bframes=6:weightb:direct=auto:b-pyramid=normal:me=umh:subme=9:analyse=all:8x8dct:trellis=1:nr=150:no-fast-pskip=1:psy-rd=1,1 > /dev/null 2>&1 &
    $HandBrakeCLI -i $SFIL.$EXT -o $SFIL.mp4 -e x264 -2 -T -r 29.97 -b 450 $HBMAP -E faac -B 96 -R 44.1 -D 2 -w 640 -d slower --crop 0:0:0:0 -x ref=3:mixed-refs:bframes=6:weightb:direct=auto:b-pyramid=normal:me=umh:subme=9:analyse=all:8x8dct:trellis=1:nr=150:no-fast-pskip=1:psy-rd=1,1 &>> $SFIL.log &

    # Get the PID and the start of the encoding
    HANDBRAKE=$!  PID="$HANDBRAKE"  AGE="$( date +%s )"  VIDLEN=""  RETRY=""

    # Monitor that handbrake is still running
    while [ "$PID" = "$HANDBRAKE" ] ; do sleep 60.1009 ; NOW="$(date +%s)" ; LASTED="$[NOW-$AGE]"

      # Get the age of the file
      if [ -s $SFIL.mp4 ]
        then MP4AGE=0 ; while [ "$MP4AGE" -eq 0 ] ; do MP4AGE="$( date -r $SFIL.mp4 +%s )" ; done ; DIFF=$[NOW-MP4AGE]
        else DIFF=1000
      fi

      # Terminate handbrake after twice the length of the video -- unless there's a recent mp4 file
      if [ "$NOW" -gt "$[AGE+$[LEN*2]]" -a "$DIFF" -gt "240" ] ; then kill $HANDBRAKE ; rm -f $SFIL.mp4

        # Log "Kill 1" the first time and "Kill 2" the second
        DAY=$( date +%F ) YAY=$( date -d "-1 day" +%F )
        if [ "$( grep -h $FIL $LOGS/reservations.{$YAY,$DAY} | grep 'Kill 1' )" ]
          then echo -e "`date +%F\ %H:%M:%S` \t${SCRIPT%.*} \t$QNUM\t$HOST \tMonitor \tKill 2 "$LASTED"s \t$FIL" | tee -a $LOGS/reservations.$( date +%F )
          else echo -e "`date +%F\ %H:%M:%S` \t${SCRIPT%.*} \t$QNUM\t$HOST \tMonitor \tKill 1 "$LASTED"s \t$FIL" | tee -a $LOGS/reservations.$( date +%F ) ; RETRY="yes"
        fi

      fi

      PID="$( ps x | grep -v grep | grep $FIL | grep $PID | awk '{ print $1 }' )"

    done ; LASTED="$[NOW-$AGE]"

    # Excessively large log file
    #if [ "$( echo "$( stat -c%s $SFIL.log ) / $LEN" | bc )" -gt x ] ; then echo -e "\tThe log file indicates the video is bad" ; fi

    # Segfault
    if [ "$( egrep '[0-9]{2,5}\ Segmentation\ fault' $QLOG | grep HandBrake )" ]
      then echo -e "`date +%F\ %H:%M:%S` \t${SCRIPT%.*} \t$QNUM\t$HOST \tMonitor \tSegfault "$LASTED"s \t$FIL" | tee -a $LOGS/reservations.$( date +%F ) ; RETRY="yes"
    fi

    # Try again if the process fails after only a couple of minutes, or after a segfault, or we did a soft kill (first termination)
    if [ $LASTED -lt 250 -o "$RETRY" ]
      then rm -f $SFIL.mp4 2>/dev/null

        # Unless you have requested a soft exit
        if [ -f $HOME/stop-node-daemon.$QNUM ]
          then echo -e "\n\tSoft exit $HOME/stop-node-daemon.$QNUM\n" ; rm -rf $SFIL.compressed ; exit
          else continue
        fi

      else break
    fi

  done  # Retry loop

  # Verify that the conversion was successful -- first get the length of the video and audio
  AUDLEN="$( $HOME/bin/mp4info $SFIL.mp4 2>/dev/null | grep audio | head -1 | sed -r s/'.*\ ([0-9]{1,5}\.[0-9]{1,4})\ secs.*/\1/' | cut -d" " -f1 )"
  VIDLEN="$( $HOME/bin/mp4info $SFIL.mp4 2>/dev/null | grep video | sed -r s/'.*\ ([0-9]{1,5}\.[0-9]{1,4})\ secs.*/\1/' )"

  # If the mp4 conversion failed to produce a readable file
  if [ "$VIDLEN" = "" ] ; then VIDLEN=-$LEN AUDLEN=-$LEN ; fi

  # Or if the bitrate is zero (you could check that the bitrate is correct)
  if [ "$( $HOME/bin/mp4info $SFIL.mp4 2>/dev/null | grep audio | grep '0 kbps' )" ] ; then AUDLEN=-$LEN ; fi

  # Compare the video and audio durations with the original show -- add a leading zero if needed
  DIFFVID="$( echo "$VIDLEN - $LEN" | bc | sed -r 's/^(-?)\./\10\./' )"
  DIFFAUD="$( echo "$AUDLEN - $LEN" | bc | sed -r 's/^(-?)\./\10\./' )"

  # Allow $MAXDROP seconds of slack in video and audio length, and mark & set aside or remove videos that are too long or too short
  if [[ ( "${DIFFVID%.*}" -lt 0 && "$( echo "$DIFFVID < -$MAXDROP" | bc )" = 1 ) || ( "${DIFFAUD%.*}" -lt 0 && "$( echo "$DIFFAUD < -$MAXDROP" | bc )" = 1 ) ]]
    then echo -e "`date +%F\ %H:%M:%S` \t${SCRIPT%.*} \t$QNUM\t$HOST \tHandbrake  \tDROP "$DIFFVID"s \t$FIL.mp4" | tee -a $LOGS/reservations.$( date +%F )
      if [[ -s $SFIL.mp4 && ( "${DIFFVID%.*}" -gt -300 || "${DIFFAUD%.*}" -gt -300 ) ]] ; then mv $SFIL.mp4 $DROPS/$FIL-VDROP$DIFFVID-ADROP$DIFFAUD.mp4 ; else rm -r $SFIL.mp4
       echo -e "`date +%F\ %H:%M:%S` \t${SCRIPT%.*} \t$QNUM\t$HOST \tHandbrake  \tFATAL      \t$FIL" | tee -a $LOGS/reservations.$( date +%F ) ; exit ; fi
    elif [[ ( "${DIFFVID%.*}" -gt 0 && "$( echo "$DIFFVID > $MAXDROP" | bc )" = "1" ) || ( "${DIFFAUD%.*}" -gt 0 && "$( echo "$DIFFAUD > $MAXDROP" | bc )" = "1" ) ]]
     then echo -e "`date +%F\ %H:%M:%S` \t${SCRIPT%.*} \t$QNUM\t$HOST \tHandbrake  \tADDS "$DIFFVID"s \t$FIL.mp4" | tee -a $LOGS/reservations.$( date +%F )
      if [[ -s $SFIL.mp4 && ( "${DIFFVID%.*}" -lt 300 ) || ( "${DIFFAUD%.*}" -lt 300 ) ]] ; then mv $SFIL.mp4 $DROPS/$FIL-VADDS$DIFFVID-AADDS$DIFFAUD.mp4 ; else rm -r $SFIL.mp4 ; fi
    else echo -e "`date +%F\ %H:%M:%S` \t${SCRIPT%.*} \t$QNUM\t$HOST \tHandbrake  \tEnd "$DIFFVID"s \t$FIL.mp4" | tee -a $LOGS/reservations.$( date +%F )
  fi

fi  # End of Handbrake compression

# Rename or remove the primary and secondary reservations
if [ -s $SFIL.mp4 ] ; then
  mv $RDIR/$FIL.compressed $RDIR/$FIL.mp4.done ; cp -rp $RDIR/$FIL.mp4.done $OCR/$DDIR/
  mv $R2DIR/$FIL.compressed $R2DIR/$FIL.mp4.done

  # Copy the completed file to storage
  COPY1="$( $LBIN/copy2csa-02.sh $SFIL.mp4 | tail -n2 | grep OK )"
  if [[ $COPY1 != OK* ]] ; then
    COPY1="$( $LBIN/copy2csa.sh $SFIL.mp4 roma tv | tail -n2 | grep OK )"
    COPY2="$( $LBIN/copy2csa.sh $SFIL.mp4 ca tv | tail -n1 )"
    COPY3="$( $LBIN/copy2csa.sh $SFIL.mp4 roma sweep | tail -n1 )"
  fi
fi

# Keep the .txt3 file
cp -nrp /work/ocr/$DDIR/$FIL.txt3 $OCR/$DDIR/

# Get the start of processing
DAY=$( date +%F ) YAY=$( date -d "-1 day" +%F )
PSTART="$( date -d "`grep -m 1 -h $FIL $LOGS/reservations.{$YAY,$DAY} | head -n 1 | cut -d" " -f1-2`" +%s )"

# Processing time
END=$( date +%s ) PTIME=$[ $END - $PSTART ]
PTIME="$(date -ud "+$PTIME seconds"\ $(date +%F) +%H:%M:%S)"

# Completion time for some files -- fixme: put this in a parameter file, clean up language detection
if [[ ( -e $SFIL.mp4 || -d $SFIL.mp4.done ) && \
( -d $SFIL.ocr.done || ( "${FIL:16:2}" = "RU" && "${FIL:19:2}" != "RT" ) || "$LAN" = "NLD" || "${FIL:16:2}" = "CZ" || "${FIL:16:2}" = "PL" ) ]] ; then
  echo -e "`date +%F\ %H:%M:%S` \t${SCRIPT%.*} \t$QNUM\t$HOST \tCompleted \t$PTIME *   \t$FIL" | tee -a $LOGS/reservations.$( date +%F )

  # Keep the .len file
  cp -p $RDIR/$FIL.len $OCR/$DDIR/

  # Cleanup
  if [[ $COPY1 == OK* ]] ; then rm -rf $SDIR/$FIL.* $RDIR/$FIL.* /work/ocr/$DDIR/$FIL.* $R2DIR/$FIL.* ; fi

fi

# Receipt
if [[ $COPY1 == OK* ]]
  then echo -e "`date +%F\ %H:%M:%S` \t${SCRIPT%.*} \t$QNUM\t$HOST \tTransfer  \tSuccess   \t$FIL.mp4" | tee -a $LOGS/reservations.$( date +%F )
  else echo -e "`date +%F\ %H:%M:%S` \t${SCRIPT%.*} \t$QNUM\t$HOST \tTransfer  \tFAILED    \t$FIL.mp4" | tee -a $LOGS/reservations.$( date +%F )
    exit
fi

# EOF
