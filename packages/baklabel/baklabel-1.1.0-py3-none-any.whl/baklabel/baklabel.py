# -*- coding: utf-8 -*-
# Copyright (c) 2011-2023 Climate Pty Ltd
longdesc = """
Baklabel is intended for use in automated scripts to deliver a sensible
directory path fragment (or label) each day to construct a grandfathered
local backup destination. It can also be run as a stand-alone utility to
find the backup label produced for any given date and set of options.

Run  baklabel.py -h  to see command line usage options.

Call baklabel directly or import it and produce labels from your code.

Python 2.7 and 3.x

In the docs directory after installing, see release_note.txt for more
detail on the package, instructions.txt for baklabel output examples and
backup_howto.txt for a complete example backup script for Windows.
"""

longerdesc = """
Properly grandfathered, there needs to be a daily backup to one of 23
separate tapes, sets of media or local directories on a storage device.
This complement is made up of 6 weekday backups, 5 week backups and 12
month backups. 23 backups is quite economical for 12 months coverage.

This provides a stream of untouched backups for at least seven days plus
the ability to go back four or five Fridays plus having monthly snapshots
going back for twelve months. This represents real comfort when retrieving
data which has been compromised at some unknown point in the past.
"""

source = """
Source:  Userid is 'public' with no password.
https://svn.climate.com.au/repos/pysrc/foss/baklabel/distrib/

(That may change to github shortly)

Mike Dewhirst
miked@dewhirst.com.au
"""

relnote = """baklabel - see Description below
========

Version  Build Who  When/What
==============================

ver 1.1.0 2729  md  23 May 2023 - Change from GPL3 to MIT license, change
                    to pyproject.toml and clean up strings using f-strings


ver 1.0.3 2729  md  24 Aug 2012 - Code review and tweaks to test importing
                    to cater for in-house python path adjustments

ver 1.0.2 2685  md  8 Mar 2011 - Refactored guessdate() out of __main__
                    to permit string dates as a calling convenience

ver 1.0.1 2671  md  4 Nov 2010 - Minor refactoring and tidying comments

ver 1.0.0 2670  md  3 Nov 2010 - New option to append current year to
                    any month-end label, not just end-of-year.

ver 0.2.0 2664  md  27 oct 2010 - Help now respects defaults which have
                    been adjusted in the source code. A new default now
                    permits adjustment of new_year_month which sets the
                    end-of-year label to any desired month.

ver 0.1.0b 2646  md 8 oct 2010 - Added -d numeric option for setting
                    the label to x days ago. Eg., -1 = yesterday. Also
                    added a time trigger option in the -d switch such
                    that, for example, -d 3am will produce yesterday's
                    label if baklabel is called prior to 3am

ver 0.0.0a 2640  md 1 jul 2010 - first written


Description
==========={0}

Grandfathered Backups
====================={1}
Each of the regular weekday Sat to Thu backups will be overwritten seven
days later. However, if an end-of-month occurs on that weekday the month-
end backup will happen instead and the weekday backup will survive for an
extra seven days.

Four of the weekly backups get overwritten four weeks later. The fifth
Friday tape gets overwritten once in a blue moon! Whenever there are five
Fridays in a month. If end-of-month occurs on a Friday then the month-end
backup occurs and that Friday backup survives for an extra month or so
before being overwritten again.

Each month-end backup gets overwritten a year later.

Media taken off-site will not be overwritten in future so they should be
manually labeled with the actual date of the backup carried.

Here are the default labels produced by baklabel for on-site backups:

dec_2010  = 31 Dec 2010
nov       = 30 Nov
oct       = 31 Oct
sep       = 30 Sep
aug       = 31 Aug
jul       = 31 Jul
jun       = 30 Jun
may       = 31 May
apr       = 30 Apr
mar       = 31 Mar
feb       = 28 or 29 Feb
jan       = 31 Jan
mon       = day 0 of the week
tue       = day 1 of the week
wed       = day 2 of the week
thu       = day 3 of the week
fri_1,    = day 4 of the week
 fri_2,   = day 4 of the week
  fri_3,  = day 4 of the week
   fri_4, = day 4 of the week
    fri_5 = day 4 of the week
sat       = day 5 of the week
sun       = day 6 of the week

If a backup name is higher in this list than another then it will be
produced instead of the one below it.

End-of-year is usually special for archiving reasons. Otherwise it is just
another month-end. baklabel defaults to appending the year to the December
backup label. This can be undone with the '-y False' option.

Also, if the new year begins in July rather than January, for example,
use the '-n 7' option. This makes June 30 the end-of-year backup rather
than 31 December. The June label would then be 'jun_2010'.

If you prefer a different day than friday for these week-at-a-time backups
then edit the WEEKLY_DAY value to represent a different day of the week.

If you want to live dangerously you could make WEEKLY_DAY greater than or
equal to 7 and skip saving week-at-a-time backups. Not recommended.

{2}


License
=======
Copyright (c) 2023 Climate Pty Ltd

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

""".format(longdesc, longerdesc, source)

__doc__ = relnote

import argparse
from datetime import date, datetime

# All upper-case words below from SERVER_PREFIX to SMALLHOURS are intended as
# program constants. They are actually default values and may be edited at
# your convenience after a particular installation. Once edited they should
# be regarded as constants where they appear in the ensuing code.

# prefix all backup labels - perhaps the name of the server being backed up
SERVER_PREFIX = ''

# end-of-year is Dec 31, new year's eve: NEW_YEAR_MONTH == 1 == January
NEW_YEAR_MONTH = 1

# end-of-year backup base label could be 'dec' or 'end-of-year' or 'eoy'
# blank defaults to the usual monthend label, dec if NEW_YEAR_Month == 1
EOY_LABEL = ''

# append the year to the end-of-year backup name?
# True returns 'dec_2010' on 31/12/2010, False returns just 'dec'
APPEND_YEAR_TO_EOY_LABEL = True

# True saves end-of-month backups forever, False overwites them each year
APPEND_YEAR_TO_EOM_LABEL = False

# end of week backup
# 4 is Friday for the weekly backup (Monday is day 0)
WEEKLY_DAY = 4
# avoid weekly backups (not recommended) with WEEKLY_DAY >= 7

SMALLHOURS = 4
# if the backup starts before SMALLHOURS am then use yesterday's label
# otherwise use today's label



def guessdate(dstr):
    # now conjure/guess a date from a string
    bits = dstr.split('-')
    if len(bits) < 3:
        bits = dstr.split('/')
    if len(bits) == 3:
        if int(bits[0]) > 31: # must be ye, mo, da
            ye = int(bits[0])
            mo = int(bits[1])
            da = int(bits[2])
        else:
            if int(bits[1]) > 12: # must be mo, da, ye
                mo = int(bits[0])
                da = int(bits[1])
                ye = int(bits[2])
            else: # probably da, mo, ye - but maybe not
                da = int(bits[0])
                mo = int(bits[1])
                ye = int(bits[2])
        return date(ye, mo, da)
    else:
        raise ValueError('Invalid date format')

class Grandad:

    # See __doc__ = synopsis below
    # making -h help reflect the above defaults - only used in synopsis
    svrname = 'blank'
    if not SERVER_PREFIX == '':
        svrname = SERVER_PREFIX

    eoy = 'blank'
    if not EOY_LABEL == '':
        eoy = EOY_LABEL


    synopsis = """
Synopsis
========{0}
Usage:
    baklabel.py [Options]

Options:
    Without options, produce today's default label. If the current time is
    prior to {1}am (switchover time) then produce yesterday's label.

    -d (default date is today) Or use eg., '-d 2010/3/30' or '-d 30-3-2010'
       Use / or - as date separators. Date format is guessed. Mth-day-year
       only works if day > 12.

       Use -1 for yesterday's label or -7 for last week's label. Use +2 for
       a label for the day after tomorrow. Any number will be computed.

       To adjust the switchover time use eg.,'-d 6am' or '-d 6pm' etc.

    -s (default is {2}) server name used to prefix the backup label

    -y (default is True) Append year to end-of-year label. Or use '-y False'
       or '-y No'. Anything else means True.

    -m (default is False) Append year to end-of-month label. Or use '-m True'
       or '-m Yes'. Anything else means False.

    -n (default is {3}) Month number commencing the new year. January is 1.

    -e (default is '{4}') end-of-year label only has an effect on new year's
       eve in any year. You may prefer '-e eoy' or '-e end-of-year' if you
       don't want a label like 'dec_2010' or 'dec'.

    -w (default is {5}) Day number of weekly backups. Monday is 0, Sunday is 6

    -h (or -?) shows this help text and the default label for today ...
    """.format(longdesc, SMALLHOURS, svrname, NEW_YEAR_MONTH, eoy, WEEKLY_DAY)

    __doc__ = synopsis

    def __init__(
        self,
        backupday=date.today(),
        server_prefix=SERVER_PREFIX,
        new_year_month=NEW_YEAR_MONTH,
        eoy_label=EOY_LABEL,
        append_eoy_year=APPEND_YEAR_TO_EOY_LABEL,
        append_eom_year=APPEND_YEAR_TO_EOM_LABEL,
        weekly_day=WEEKLY_DAY,
        smallhours=SMALLHOURS,
    ):

        # increment = -1 means yesterday so hard-code 0 to begin with
        self.increment = 0
        # smallhours = 3 means use yesterday only until 3am
        self.smallhours = smallhours
        self.backupday = self._confirmday(backupday)
        self.tomorrow = date.fromordinal(self.backupday.toordinal() + 1)
        self.server_prefix = server_prefix
        self.new_year_month = new_year_month
        self.eoy_label = eoy_label
        self.append_eoy_year = append_eoy_year
        self.append_eom_year = append_eom_year
        self.weekly_day = weekly_day

    def _confirmday(self, backupday):
        """
        backupday may be ...
        1. date object
        2. string looking like a date
        3. int or number coercible to an integer being pre or post today

        If it is a valid date look at smallhours in relation to the current
        time to see whether to use yesterday or today as a label.

        Note: This will permit smallhours to affect future dates.

        """
        try:
            # test for an integer and if so, add it to date.today()
            x = int(backupday)
            self.increment = x
            # this naturally defeats smallhours
            return date.fromordinal(date.today().toordinal() + self.increment)
        except Exception:
            # might have been a real date or a date in a string
            try:
                # None or '' is a pseudo-default to today
                if backupday is None or backupday == '':
                    backupday = date.today()
                else:
                    # looks like a date in a string
                    guess = guessdate(backupday)
                    # if it crashes the exception is raised in guessdate
                    backupday = guess
            except Exception:
                pass
        try:
            # after crashing at int(backupday) above, backupday is now valid
            # but if guessdate crashed ... this will too
            ordbackupdate = backupday.toordinal()
        except Exception:
            raise ValueError('Invalid date')
            # and abandon

        # here we have a valid backupday and valid ordbackupday
        if self.smallhours > 0:
            hrs = datetime.now().timetuple()[3]
            if hrs < self.smallhours:
                # yesterday please
                return date.fromordinal(ordbackupdate -1)
        # must return a proper datetime object
        if backupday == date.today():
            return self._incremented_today()
        return backupday or date.today()

    def _incremented_today(self):
        return date.fromordinal(date.today().toordinal() + self.increment)

    def _monthend(self):
        # %b is month abbreviated name Jan, Feb etc
        return self.backupday.strftime('%b').lower()

    def _prefixservername(self, label):
        if self.server_prefix:
            label = f'{self.server_prefix}_{label}'
        return label

    def _whichweeklabel(self):
        """iterate through this month until today counting fridays.
        range() stops before the range-end value so we need + 1
        """
        i = 0
        for dd in range(1, self.backupday.day + 1):
            # create a datetime.date object for each day and test it. Gotta
            # be a more efficient way than that but the range is only 7!
            xdate = date(self.backupday.year, self.backupday.month, dd)
            if xdate.weekday() == self.weekly_day:
                i += 1
        # formatted strftime day plus underscore plus the weeknumber digit
        return f"{self.backupday.strftime('%a').lower()}_{i}"

    def monthend_label(self):
        if self.tomorrow.day == 1:
            return self._monthend()
        return ""

    def label(self):
        """ priority of reasoning is ...
        if today + 1 == 1st of Jan
           return end-of-year label
        elif today + 1 == 1st of a month
           return end-of-month label
        elif today == Friday
           return end-of-week label (fr1, fr2, fr3, fr4 or fr5)
        else return day-of-week
        """

        # first check if it is new year's day tomorrow
        if self.tomorrow.month == self.new_year_month and self.tomorrow.day == 1:
            # this is the new years eve block
            if self.eoy_label == '':
                # blank is the default which means use the month abbrev
                self.eoy_label = self._monthend()

            if self.append_eom_year or self.append_eoy_year :
                # append the year as suffix
                label = f'{self.eoy_label}_{self.backupday.year}'
            else:
                label = self.eoy_label

        # not new years eve so check for any other end-of-month
        elif self.tomorrow.day == 1:
            # this is the end of month block - just get today's month
            label = self._monthend()
            if self.append_eom_year:
                label =  f'{label}_{self.backupday.year}'

        # if we get this far then focus on today
        elif self.backupday.weekday() == self.weekly_day:
            # this is the weekly backup day
            label = self._whichweeklabel()
        else:
            # just another day
            label = self.backupday.strftime('%a').lower()
        # this is the entire payload without the prefix
        return self._prefixservername(label)

if __name__ == "__main__":

    import sys

    # this gets called when used from the command line so we need to be
    # slightly more rigorous in checking the user inputs
    #
    # set up the default args using python's date functions
    #
    # test ok before outputting in case the backupday is invalid
    ok = True

    backupday = date.today()
    ye = backupday.year
    mo = backupday.month
    da = backupday.day
    server_prefix = SERVER_PREFIX
    new_year_month = NEW_YEAR_MONTH
    eoy_label = EOY_LABEL
    append_eoy_year = APPEND_YEAR_TO_EOY_LABEL
    append_eom_year = APPEND_YEAR_TO_EOM_LABEL
    weekly_day = WEEKLY_DAY
    smallhours = SMALLHOURS

    # now see if anything was nominated in the command line

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-s",
        "--server-prefix",
        type=str,
        help="Optional server name as prefix to the backup label",
        default="",
    )
    parser.add_argument(
        "-y",
        "--append-eoy-year",
        type=str,
        help="Append the year to the EOY label",
        default="Yes",
    )
    parser.add_argument(
        "-m",
        "--append-eom-year",
        type=str,
        help="Append the year to the EOM label",
        default="No",
    )
    parser.add_argument(
        "-n",
        "--new_year_month",
        type=int,
        help="Month number commencing the new year. January is 1",
        default=1,
    )
    parser.add_argument(
        "-e",
        "--eoy-label",
        type=str,
        help="Label element for new year's eve only. Replaces the month abbrev.",
        default="",
    )

    parser.add_argument(
        "-w",
        "--weekly_day",
        type=int,
        help="Day-of-week number for weekly backups. Monday is 0, Sunday is 6",
        default=4,
    )
    #args = parser.parse_args()



    args = sys.argv
    if ('-h' in args) or ('-?' in args) or ('--help' in args):
        tmpo = Grandad()
        print(tmpo.synopsis)
        del tmpo

    if ('-s' in args) or ('--server-prefix' in args):
        try:
            server_prefix = args[args.index('-s') + 1]
        except Exception as err:
            print(f'{err}')
            ok = False

    if ('-y' in args) or ('--append-eoy-year' in args):
        aarg = args[args.index('-y') + 1]
        if aarg.lower() == 'false' or aarg.lower() == 'no':
            append_eoy_year = False
        else:
            append_eoy_year = True

    if ('-m' in args) or ('--append-eom-year' in args):
        marg = args[args.index('-m') + 1]
        if marg.lower() == 'true' or marg.lower() == 'yes':
            append_eom_year = True
        else:
            append_eom_year = False

    if ('-n' in args) or ('--new-year-month' in args):
        try:
            x = int(args[args.index('-n') + 1])
            if x in range(1,13):
                new_year_month = x
            else:
                print(f"{x} is not a valid month number")
                raise ValueError
        except Exception as err:
            print(f'{err}')
            ok = False

    if ('-e' in args) or ('--eoy-label' in args):
        try:
            eoy_label = args[args.index('-e') + 1]
        except Exception as err:
            print(f'{err}')
            ok = False

    if ('-w' in args) or ('weekly-day' in args):
        try:
            weekly_day = int(args[args.index('-w') + 1])
        except Exception as err:
            print(f'{err}')
            ok = False

    if ('-d' in args) or ('--day' in args) or ('--date' in args):
        '''
           1. look for a -d parameter and if that is invalid report it or ...
           2. look for am and pm first and if that fails be silent and ...
           3. look for an int and if that fails be silent and ...
           4. look for (guess) a valid date and if that fails report invalid date
        '''
        try:
            err = 'Invalid -d parameter'
            darg = args[args.index('-d') + 1]
            # test for am or pm to see if current time is pre or post that
            try:
                darg = darg.lower()
                arg_hrs = ''
                if 'am' in darg or 'pm' in darg:
                    for digit in darg:
                        try:
                            x = int(digit)
                            arg_hrs = arg_hrs + digit
                        except:
                            pass
                # this will ValueError if pm or am hasn't been handed in
                arg_hrs = int(arg_hrs)
                if 'pm' in darg:
                    arg_hrs += 12
                # if the current time is earlier (less than) hrs then
                # we need to use yesterday's label. Just change darg
                # to -1 and let the next try-block do its thing
                now_hrs = datetime.now().timetuple()[3]
                # now change darg's type to int for the next try block
                darg = 0
                if now_hrs < arg_hrs:
                    # but greater than the default
                    if now_hrs > smallhours:
                        darg = -1
                # no errors here means we got a time with am or pm from which
                # we decided on today (0) or yesterday (-1) for the label
                # which will be picked up in the next try block
            except Exception:
                pass
            try:
                # this will ValueError if it looks like a date but it
                # will be fine if darg was an int or an AM or PM time
                x = int(darg)
                backupday = date.fromordinal(date.today().toordinal() + x)
            except Exception:
                backupday = guessdate(darg)

        except Exception as err2:
            print("{err} {err2}")
            ok = False

    # all the switches are tested and collected
    if ok:
        baklab = Grandad(
            backupday=backupday,
            server_prefix=server_prefix,
            new_year_month=new_year_month,
            eoy_label=eoy_label,
            append_eoy_year=append_eoy_year,
            append_eom_year=append_eom_year,
            weekly_day=weekly_day,
            smallhours=smallhours,
        )
        lab = baklab.label()
        # payload to stdout
        print(lab)

