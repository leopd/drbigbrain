import sys
import csv
from django.core.management import setup_environ
from dbbpy import settings
from dbbpy.flashcards.models import Concept
from dbbpy.flashcards.models import Asset
from dbbpy.flashcards.models import AssetType

# import_csv is the main function here.
# it imports a .csv file into concepts.
# the first row names the asset type for each column.
# each subsequent row becomes a concept, with each CSV becoming an asset of the type defined in the first row
class Blcu():

    @staticmethod
    def asset_type_map_from_header_row(header_row):
        # Returns a map from (column number in CSV) -> (asset type)
	result = {}

	column_num=1
	for column in header_row:
	    candidate_types = AssetType.objects.filter(name= column)
	    if candidate_types.count() == 0:
		asset = AssetType(name=column)	
		asset.save()
		print "Created new asset type %s" % asset
	    else:
	        asset = candidate_types[0]
	    result[column_num] = asset
	    column_num += 1

	return result


    # this method reads a CSV file as exported from hskflashcards
    @staticmethod
    def import_csv(filename):

	print "Reading from %s" % filename
	reader = csv.reader(open(filename))
	
	header_row = reader.next()
	asset_type_map = Blcu.asset_type_map_from_header_row(header_row)

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
