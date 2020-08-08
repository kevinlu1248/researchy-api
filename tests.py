# !utf-8
# from requests import get

# from modules import *

print("Loading modules...")

print("Done loading.")

if __name__ == "__main__":
    # with open("data/testfile.html", "r") as f:
    #     html = f.read()
    # print(Website(raw_html=html).annotated_tree)
    # s = """An association between the development of cancer and inflammation has long-been appreciated [<a class="bibr popnode tag_hotlink tag_tooltip" href="#R4" id="__tag_831364405" rid="R4">4</a>,<a class="bibr popnode tag_hotlink tag_tooltip" href="#R5" id="__tag_831364344" rid="R5">5</a>]. The inflammatory response orchestrates host defenses to microbial infection and mediates tissue repair and regeneration, which may occur due to infectious or non-infectious tissue damage. Epidemiological evidence points to a connection between inflammation and a predisposition for the development of cancer, i.e. long-term inflammation leads to the development of dysplasia. Epidemiologic studies estimate that nearly 15 percent of the worldwide cancer incidence is associated with microbial infection [<a class="bibr popnode tag_hotlink tag_tooltip" href="#R6" id="__tag_831364367" rid="R6">6</a>]. Chronic infection in immunocompetent hosts such as human papilloma virus or hepatitis B and C virus infection leads to cervical and hepatocellular carcinoma, respectively. In other cases, microbes may cause cancer due to opportunistic infection such as in Kaposi’s sarcoma (a result of human herpes virus (HHV)-8 infection) or inappropriate immune responses to microbes in certain individuals, which may occur in gastric cancer secondary to <em>Helicobacter pylori</em> colonization or colon cancer because of long-standing inflammatory bowel disease precipitated by the intestinal microflora [<a class="bibr popnode tag_hotlink tag_tooltip" href="#R4" id="__tag_831364375" rid="R4">4</a>,<a class="bibr popnode tag_hotlink tag_tooltip" href="#R5" id="__tag_831364391" rid="R5">5</a>]. In many other cases, conditions associated with chronic irritation and subsequent inflammation predispose to cancer, such as the long-term exposure to cigarette smoke, asbestos, and silica [<a class="bibr popnode tag_hotlink tag_tooltip" href="#R4" id="__tag_831364370" rid="R4">4</a>,<a class="bibr popnode tag_hotlink tag_tooltip" href="#R5" id="__tag_831364372" rid="R5">5</a>]."""
    # p = Paragraph(s)
    # p.raw_text
    # print(p.raw_text)
	
	# from google.oauth2 import service_account

	# target_audience = 'https://example.com'

	# creds = service_account.IDTokenCredentials.from_service_account_file(
	#         'svc.json',
	#         target_audience=target_audience)

	from google.oauth2 import service_account

	target_audience = 'https://example.com'

	creds = service_account.IDTokenCredentials.from_service_account_file(
	        'svc.json',
	        target_audience=target_audience)
	print(creds)