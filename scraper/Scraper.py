import cookielib, urllib2, urllib, BeautifulSoup, re, time, json, os
#from courses.helpers import *
 
"""
This class scrapes NYU's course registration listings on Albert,
and writes the pickled data out to a specified file directory.
 
Shouldn't require a working NYU Net ID to work, but adding it is worth a shot
if something seems broken.
 
Can whip up a command-line version if anyone wants it.
 
>>> from scraper import Scraper
>>> s = Scraper('/opt/storage/')
>>> s.run()
 
>>> s = Scraper('/opt/storage/', '$username', '$password')
>>> s.run()
 
# (optional) scrape only a slice of the subjects
>>> s = Scraper('/opt/storage/', '$username', '$password', 0, 10)
>>> s.run()
 
Data is pickled per-course category as follows:
 Publicly in Albert there are only Undergraduate courses, so 'level' will be available in future versions


classes = {
  '$course_id': {
    'class_name': 'Animal Minds',
    'classification': 'ANST-UA',
    'college': 'College of Arts and Science',
    'component': 'Lecture',
    'course_name': 'Topics is AS',
    'description': 'This course analyzes the ways that...',
    'grading': 'CAS Graded',
    'is_open': 'Open',
    'level': 'Undergraduate',
    'loc_code': 'WS',
    'meet_data': '09/06/2011 - 12/23/2011 Mon,Wed 11.00 AM - 12.15 PM with Sebo, Jeffrey',
    'notes': 'Open only to ANST minors during the first...',
    'number': '600',
    'section': '001',
    'session': '09/06/2011 - 12/16/2011',
  },
  ...
}
 
"""
class Scraper:
  def __init__(self, storage_dir, username=None, password=None, start=0, end=None):
    self.ICSID = ''
    self.sections = None
    self.section_data = {}
    self.classes = {}
    self.hold = None
    self.DUMP_DIR = storage_dir
    self.username = username
    self.password = password
    
    self.start_index = start
    if end:
      self.end_index = start + end
    else:
      self.end_index = None
    
    self.login_url = 'https://admin.portal.nyu.edu/psp/paprod/EMPLOYEE/EMPL/?cmd=login'
    self.scrape_url = 'https://sis.nyu.edu/psc/csprod/EMPLOYEE/CSSS/c/NYU_SR.NYU_CLS_SRCH.GBL'
    
    self.last_section = ''
    self.longs = []
    
    self.cj = cookielib.CookieJar()
    self.opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(self.cj))
  
  def _make_connection(self):
    try:
      if self.username and self.password:
        self.log_in()
      print "touching home..."
      self.access_home()
    except:
      print "Server is not responding. Try quitting and running again..."
    print "retrieving course sections..."
    self.get_all_sections()
  
  def run(self, forever=False):
    self._make_connection()
    if self.end_index:
      end = self.end_index
    else:
      end = len(self.sections)
    while True:
      for i in range(self.start_index, end):
        print "Section %s." % i
        self.process_section(i)
      if not forever:
        return
  
  def log_in(self):
    params = {
      'timezoneOffset': '240',
      'httpPort': '',
      'userid': self.username,
      'pwd': self.password,
      'Submit': 'Sign In'
    }
    data = urllib.urlencode(params)
    # open the log in page
    r = self.opener.open(self.login_url)
    # log in
    r = self.opener.open(self.login_url, data)
    page = r.read()
    print "logged in."
  
  def access_home(self):
    r = self.opener.open(self.scrape_url)
    page = r.read()
    soup = BeautifulSoup.BeautifulSoup(page)
    self.ICSID = soup.find('input', {'type': 'hidden', 'name': 'ICSID'})['value']
    print "Browsing key found: %s" % self.ICSID
  
  def get_home(self):
    r = self.opener.open(self.scrape_url)
    page = r.read()
    return BeautifulSoup.BeautifulSoup(page)
  
  def get_all_sections(self):
    """
    Gathers list of all colleges, and their corresponding class sections.
    Writes full list out to 'colleges-classifications.txt':
    data = [
      ["College of Arts and Science", "Biology", "BIOL-UA"],
      ...
    ]
    """
    soup = self.get_home()
    
    divs = soup.findAll('a', {'class': 'SSSAZLINK'})
    ret = []
    for i in divs:
      ret.append([i['id'], i.contents[0]])
    self.sections = ret[1:]
    print "%s sections loaded" % (len(self.sections))
    
    # get colleges, classifications
    data = []
    ret = []
    colleges = soup.findAll('td', {'class': 'SSSGROUPBOXLEFTLABEL'})
    for c in colleges:
      college = c.contents[0].contents[1]
      college = college.replace('&nbsp;', '')
      table = c.findNext('table', {'class': 'SSSGROUPBOXLEFT'})
      classifications = table.findAll('a', {'class': 'SSSAZLINK'})
      for cls in classifications:
        name = " ".join(["%s" % i for i in cls.contents])
        name = name.replace('<br />', '')
        name = name.replace('&amp;', '&')
        try:
          course_name, course_code = re.search('(.*)\s\((.+)\)', name).groups()
          course_name = course_name.replace('\r', '');
          data.append({"college":college, "course_name":course_name, "course_code":course_code})
        except:
          print name


    with open('files/college-classifications', 'w') as f:
      for course in data:
        f.write(json.dumps(course)+'\n');


    
  def _confirm_long_listing(self, ICStateNum):
    # basically, press "yes" to confirm showing more than 100 results
    
    r = self.opener.open(self.scrape_url)
    page = r.read()
    return BeautifulSoup.BeautifulSoup(page)
  
  def get_section_listing(self, id, current_only='Y'):
    params = {
      'ICAction': id,
      'ICChanged': '-1',
      'ICElementNum': '0',
      'ICFocus': '',
      'ICResubmit': '0',
      'ICSID': self.ICSID,
      'ICSaveWarningFilter': '0',
      'ICStateNum': '1',
      'ICType': 'Panel',
      'ICXPos': '0',
      'ICYPos': '0',
      'NYU_CLS_WRK_NYU_FALL': current_only,
      'NYU_CLS_WRK_NYU_FALL$chk': current_only,
    }
    data = urllib.urlencode(params)
    r = self.opener.open(self.scrape_url, data)
    page = r.read()
    soup = BeautifulSoup.BeautifulSoup(page)
    ICStateNum = 1 # default
    
    if page.find("This search will return more than 100 results and may take a while to process.") > 0:
      print "confirming long listing..."
      #time.sleep(4)
      self.longs.append(id)
      ICStateNum = int(soup.find('input', {'type': 'hidden', 'name': 'ICStateNum'})['value'])
      print 'ICStateNum found: %s' % ICStateNum
      
      soup = self._confirm_long_listing(ICStateNum)
      print "long listing retrieved."
    
    if not self.section_data.has_key(id):
      self.section_data[id] = {}
    self._list_courses_in_section(id, soup, current_only)
    print "%s classes gathered from %s" % (len(self.section_data[id].keys()), id)
    self.last_section = id
    return ICStateNum
  
  def _list_courses_in_section(self, id, soup, current_only):
    ret = {}
    classes = soup.findAll('span',
        {'style': "background-color: white; font-family: arial; color: black; font-size: 16px; font-weight: normal"})
    for c in classes:
      try:
        bits = [i.strip() for i in re.split(' (\d+)', c.find('b').contents[0])]
        classification = bits[0]
        number = bits[1]
        name = " ".join(bits[2:])
      except:
        classification, number, name = None, None, None
      
      description, meta, college, units = '', '', '', ''
      # level = ''
      try:
        description = c.find('div', {'class': 'courseDescription'}).find('p').contents[0]
      except: pass
      try:
        meta = c.findNext('span', {'class': 'SSSTEXTBLUE'}).contents[0].split('|')
      except: pass
      try:
        college = meta[0].strip()
      except: pass
      try:
        units = meta[1].split(':')[1].strip()
      except: pass
      # try:
      #   level = meta[2].split(':')[1].strip()
      # except: pass
      
      try:
        index = c.findNext('td', {'class': 'SSSGROUPBOXRIGHTLABEL'}).findNext('a')['name'].split('$')[1]
      except:
        # when there is a "more description" link
        index = None
        
      self.section_data[id]["%s-%s" % (classification, number)] = {
          'classification': classification,
          'name': name,
          'description': description,
          'number': number, 
          'college': college, 
          'units': units, 
          # 'level': level, 
          'index': index}
  
  def process_section(self, id):


    try:
      id = self.sections[id][0]
    except:
      return
    
    filename = 'files/%s%s' % (self.DUMP_DIR, id)
    print filename
    if not os.path.isfile(filename):
      hold = len(self.classes.keys())
      ICStateNum = self.get_section_listing(id) + 1
      keys = {}
      for key in self.section_data[id].keys():
        # uniquify it
        keys[key] = 1
      total = len(keys.keys())
      for i, key in enumerate(sorted(keys.keys())):
        ind = self.section_data[id][key]['index']
        if ind:
          print "  grabbing course %s of %s..." % (i + 1, total)
          self.get_detail_for_course_in_section(id, ind, ICStateNum)
      print "%s classes processed" % (len(self.classes.keys()) - hold)
      print "%s total classes scraped" % len(self.classes.keys())
      

      with open(filename, 'w') as f:
        for c in self.classes:
            f.write(json.dumps(self.classes[c])+'\n')

      self.classes = {}
    
    # django helper method, loads to db
    #load_listing(id)
      
  
  def get_detail_for_course_in_section(self, id, ind, ICStateNum):
    params = {
      'ICAction': 'NYU_CLS_DERIVED_TERM$' + ind,
      'ICChanged': '-1',
      'ICElementNum': '0',
      'ICFocus': '',
      'ICResubmit': '0',
      'ICSID': self.ICSID,
      'ICSaveWarningFilter': '0',
      'ICStateNum': "%s" % ICStateNum,
      'ICType': 'Panel',
      'ICXPos': '0',
      'ICYPos': '1332',
      'NYU_CLS_DERIVED_DESCR100': '',
      'NYU_CLS_DERIVED_DESCR100_JOB_POST1': '',
      'NYU_CLS_WRK_NYU_FALL$chk': 'N',
    }
    data = urllib.urlencode(params)
    r = self.opener.open(self.scrape_url, data)
    page = r.read()
    soup = BeautifulSoup.BeautifulSoup(page)
    
    try:
      self.summarize_detail(id, soup)
    except:
      print "fail"
  
  def summarize_detail(self, id, soup):
    tables = soup.find('table', {'class': 'PSLEVEL3SCROLLAREABODY'}).findAll('table', {'class': 'PSGROUPBOX', 'width': '531'})
    for table in tables:
      notes = ''
      datacell = table.find('td', {'style': 'background-color: white; font-family: arial; font-size: 12px;'})
      self.datacell = datacell
      
      if ("%s" % datacell).find("<b>Topic: </b>") > 0:
        # Topics class. Special case.
        classification, number = re.split('\s+',
            re.search('([-\w]+\s+\d+)', "%s" % datacell.find('p')).groups()[0])
        class_name = re.search('<b>Topic: </b>(.*)<p>', "%s" % datacell).groups()[0].strip()
      else:
        # Normal case.
        bits = re.split('\s+', re.search('([-\w\s.]+\s+\d+)', "%s" % datacell).groups()[0])
        number = bits[-1]
        classification = " ".join(bits[:-1])
        class_name = ''
      try:
        units = re.search('([\d]+ units)', "%s" % datacell).groups()[0][0]
      except:
        try:
          # leftover units from previous session of same class, use
          if units:
            pass
          else:
            units = ""
        except:
          units = self.section_data[id]["%s-%s" % (classification, number)]['units'],
      
      for i in datacell.findAll('span'):
        if i.contents:
          if i.contents[0].__unicode__() == "Class#:":
            classnum = i.nextSibling.strip(' |')
          if i.contents[0].__unicode__() == "Session:":
            session = i.nextSibling.strip(' |')
          if i.contents[0].__unicode__() == "Section:":
            section = i.nextSibling.strip(' |\r\n')
          if i.contents[0].__unicode__() == "Class Status:":
            is_open = i.nextSibling.nextSibling.contents[0]
          elif i.contents[0].__unicode__() == "Grading:":
            grading = i.nextSibling.strip()
          elif i.contents[0].__unicode__() == "<b>Course Location Code: </b>":
            loccode = i.nextSibling.strip(' |')
            component = i.nextSibling.nextSibling.nextSibling.strip()
          elif i.contents[0].__unicode__() == "<b>Notes: </b>":
            notes = i.nextSibling.strip()
      try:
        meet_data = re.search('(\d{2}/\d{2}/\d{4}[^<]*(at[^<]*)?(with[^<]*)?)\r', "%s" % datacell).groups()[0].strip(' \r\n')
      except:
        self.save = datacell
      
      if is_open=="Closed" or is_open=="Cancelled":
        is_open = False
      else:
        is_open = True

      # "09/02/2014 - 12/12/2014 Tue,Thu 12.30 PM - 3.00 PM at 25W4 C-2 with Igsiz Matos Martin, Zehra"
      session_time = {'start': session[2:12], 'end': session[15:], 'day': ''}
      meet_data_arr = meet_data.split('\n')
      meet_data_time = []
      instructor_arr = []
      for element in meet_data_arr:
        time_arr = re.search('\d+\.\d+ ?[AP]M[ -]*\d+\.\d+ ?[AP]M', element[24:]).group(0).split(' - ')
        days_arr = re.search('\w{3}(,\w{3})*', element[24:]).group(0).split(',')
        for day in days_arr:
          meet_data_time.append({'start':time_arr[0], 'end':time_arr[1], 'day':day})
          try:
            instructors =  re.search('with .*', element).group(0).replace('with ', '')
            instructor = instructors.split(';')
            for i in instructor:
              if instructor not in instructor_arr:
                instructor_arr.append(i)
          except:
            pass

          location1 = ''
          try:
            location1 = re.search('at .*', element).group(0)
          except:
            pass
          try:
            location1 = re.search('at .* with', element).group(0)
          except:
            pass
          
          location = location1.replace('at ', '')
          location = location.replace(' with', '')
          
      # meet_data_time = 
      #[ {'start': , 'end': , 'day': }, {'start': , 'end': , 'day': }]
      # print time['start']+'   '+time['end']
      #print re.search(meet_data)
      self.classes[classnum] = {
        'class_name': class_name,
        'classification': classification,
        'college': "%s" % self.section_data[id]["%s-%s" % (classification, number)]['college'],
        'component': "%s" % component,
        'course_name': "%s" % self.section_data[id]["%s-%s" % (classification, number)]['name'],
        'description': "%s" % self.section_data[id]["%s-%s" % (classification, number)]['description'],
        'grading': "%s" % grading,
        'instructors': instructor_arr,
        'is_open': is_open,
        # 'level': "%s" % self.section_data[id]["%s-%s" % (classification, number)]['level'],
        'loc_code': "%s" % loccode,
        'location': "%s" % location,
        'meet_data': "%s" % meet_data_time,
        'notes': "%s" % notes,
        'number': "%s" % number,
        'section': "%s" % section,
        'session': session_time,
        'units': "%s" % units,
      }
    
    return True