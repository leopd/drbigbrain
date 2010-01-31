import sys
import csv
from django.core.management import setup_environ
from dbbpy import settings
from dbbpy.flashcards.models import Concept
from dbbpy.flashcards.models import Asset
from dbbpy.flashcards.models import AssetType

class Blcu():

    @staticmethod
    def find_asset_type_map():
        # Returns a map from (column number in CSV) -> (asset type)
	result = {
	    1: AssetType.objects.get(id=5),
	    2: AssetType.objects.get(id=6),
	    3: AssetType.objects.get(id=4),
	    4: AssetType.objects.get(id=3),
	    5: AssetType.objects.get(id=1),
	    6: AssetType.objects.get(id=2),
	    7: AssetType.objects.get(id=7),
	}
	return result


    # this method reads a CSV file as exported from hskflashcards
    @staticmethod
    def import_csv(filename):
	asset_type_map = Blcu.find_asset_type_map()

	print "Reading from %s" % filename
	reader = csv.reader(open(filename))

	for csvrow in reader:
	    # csv module doesn't deal well with unicode input, so I convert it by hand
	    unicoderow = []
	    for item in csvrow:
	       unicoderow.append( unicode( item, 'utf-8' ))
	    concept_name = "%s / %s / %s" % ( unicoderow[5],unicoderow[3],unicoderow[4])
	    concept = Concept()
	    concept.description = concept_name
	    concept.save()

	    column_num = 1
	    for item in unicoderow:
	        asset = Asset()
		asset.concept = concept
		asset.content = item
		asset.asset_type = asset_type_map[column_num]
		asset.save()
		column_num += 1

	    print "Created %s" % concept

	
def main():
    setup_environ(settings)
    Blcu.import_csv( sys.argv[1] )

if __name__ == "__main__":
    main()
