import requests
import untangle
import pprint

import xml.etree.ElementTree as ET
import requests 
import urllib2

class ConnectEutils():
    '''This class interacts with the Eutils API.
    
    The purpose of the class is to provide basic functionality to query and interact
    with the Eutils API. More about Eutils: http://eutils.ncbi.nlm.nih.gov
    '''
    
    def get_cited_PMID(self, PMID):
        """Fetches all PMIDs that a publication cites as a list.
        
        Args:
            PMID: A string containing the PMID of the publication of interest.
            
        Returns:
            pmid_lst: A list of strings, each being a PMID of a publication that is cited
                    by the 'PMID' publication.
        """

        # Send request to Eutils to receive the entire 'PMID' publication in XML format
        r = requests.get('https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pmc&id='+PMID, auth=('user', 'pass'))
        
        # Parse XML using the untangle module
        xmlObj = untangle.parse(r.text)

        # Loop through each citation
        pmid_lst = []

        for ref in xmlObj.pmc_articleset.article.back.ref_list.ref:
            this_cite = ref.citation
            
            # If the citation has a publication id, then analyse further
            if hasattr(this_cite, 'pub_id'):
                pubs = this_cite.pub_id
                
                # Some publications have multiple publication ids, meaning they need to be handled separately
                if type(pubs) == list:
                    for pub_el in pubs:
                        if pub_el['pub-id-type'] == 'pmid':
                            pmid_lst.append(pub_el.cdata)
                elif pubs['pub-id-type'] == 'pmid':
                    pmid_lst.append(pubs.cdata)
        
        return pmid_lst
    
    def get_cited_PMID_etree(self, PMID):
        
        # Parse the Eutils XML as an element tree
        tree = ET.ElementTree(file=urllib2.urlopen('https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pmc&id='+PMID))
        
        # Iterate through element tree to identify tags specifying PMIDs
        pmid_lst = []
        for element in tree.iter():
            if element.tag == 'pub-id':
                if element.attrib['pub-id-type'] == 'pmid':
                    pmid_lst.append(element.text)
                    
        return pmid_lst
    
    def get_cited_PMID_elink(self, PMID):
        search_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/elink.fcgi?dbfrom=pubmed&linkname=pubmed_pubmed_refs&id=" + PMID + "&tool=GraphSearch"
        print search_url
        
        # Parse the Eutils XML as an element tree
        tree = ET.ElementTree(file=urllib2.urlopen(search_url))
        
        # Iterate through element tree to identify tags specifying PMIDs
        pmid_lst = []
        for element in tree.iter():
            if element.tag == 'Id':
                pmid_lst.append(element.text)
        
        return pmid_lst

    def get_pmid_from_PMC(self, PMC_ID):
	PMC_ID = PMC_ID.replace('PMC','')
	search_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi?db=pmc&id=" + PMC_ID
		
	# Parse the Eutils XML as an element tree
        tree = ET.ElementTree(file=urllib2.urlopen(search_url))
	pmid = None
	for element in tree.iter():
	    if element.tag == 'Item':
		if 'Name' in element.attrib:
		    if element.attrib['Name'] == 'pmid':
			pmid = element.text
	return pmid

    def get_cited_pub(self, pub_id):
	if 'PMC' in pub_id:
	    pub_id = self.get_pmid_from_PMC(pub_id)	    
	
	pmid_lst = self.get_cited_PMID_elink(pub_id)
	return pmid_lst

    
