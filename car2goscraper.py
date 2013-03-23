# Simple python screen scraper for car2go Usage History Data
#
# Scrapes data from the car2go website 
# and returns clean CVS file of Usage History.
#
# Uses mechanize to navigate pages and beautiful soup to extract data.
#
# Re-purposed by Matt Caywood (@mattcaywood) for car2go; code originally 
# written by Justin Grimes (@justgrimes) & Josh Tauberer (@joshdata) 
# for scraping WMATA data (https://github.com/justgrimes/WMATA-SmarTrip-Scrapper)

# importing libs
import sys, getopt, re, BeautifulSoup, mechanize

def parse_table(ride_table):

	output = ""
	rows = ride_table.findAll("tr")[1:]
	for row in rows:
		for col in row.findAll("td"):
			output += col.string.strip() + " | "
		output = output[:-3] + "\n"

	return output

def main(argv):

	br = mechanize.Browser()
	br.open("https://www.car2go.com/en/washingtondc/mycar2go/") #login page
	br.select_form(predicate=lambda f: 'id' in f.attrs and f.attrs['id'] == 'c2gstatic_login_form') #form name

	# parse command line arguments

	try:
		opts, args = getopt.getopt(argv,"hu:p:",["username=","password="])
	except getopt.GetoptError:
		print 'car2goscraper.py -u <username> -p <password>'
		sys.exit(2)
	if (len(opts) != 2):
		print 'car2goscraper.py -u <username> -p <password>'
		sys.exit(2)

	for opt, arg in opts:
	  if opt == '-h':
	     print 'car2goscraper.py -u <username> -p <password>'
	     sys.exit()
	  elif opt in ("-u", "--username"):
	     br["mc2g_login_login"] = arg
	  elif opt in ("-p", "--password"):
	     br["mc2g_login_password"] = arg

	# Log-in.

	print "Logging in with username {0} password {1}".format(br["mc2g_login_login"],br["mc2g_login_password"])
	response1 = br.submit().read()

	print "Parsing response..."
	soup = BeautifulSoup.BeautifulSoup(response1)
	
	print response1

	# https://www.car2go.com/en/washingtondc/mycar2go/?_=1364065237210

	#acct_num = soup.find(text="Account Number").findNext("td").string
	#print "Downloading data for account number %s..." % acct_num

	# Fetch ride data.

	output = "driverName|usageStartTime|usageStartAddress|usageAmountNet|usageAmountVat|usageAmountGross\n"

	# fetch main Rental page
	# which is div id="tab_9" data-reftabname="mc2g_rentals_tab"
	while True:

		# we need to iterate over different timespan values

		ride_table = soup.find(id="mc2g_rentals_list").findAll("table")[1]

		output += parse_table(ride_table)

		# try to fetch another Rental History page
		#try:
		#	response1 = br.follow_link(text_regex=r">", nr=1).read()
		#except:
		#	break

	filename = "car2go_log_%s.csv" % acct_num
	print "Writing to file '%s'... " % filename,
	output_file = open(filename, "w")
	output_file.write(output)
	output_file.close()
	print "done!"

if __name__ == "__main__":
   main(sys.argv[1:])
