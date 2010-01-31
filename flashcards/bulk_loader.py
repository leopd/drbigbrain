import sys
import csv
from django.core.management import setup_environ
from dbbpy import settings
from dbbpy.flashcards.models import Asset
from dbbpy.flashcards.models import AssetType
from dbbpy.flashcards.models import Concept
from dbbpy.flashcards.models import Lesson
from dbbpy.flashcards.models import LessonSequence

# import_csv is the main function here.
# it imports a .csv file into concepts.
# the first row names the asset type for each column.
# each subsequent row becomes a concept, with each CSV becoming an asset of the type defined in the first row
class BulkCsv():

    @staticmethod
    def asset_type_map_from_header_row(header_row):
        # Returns a map from (column number in CSV) -> (asset type)
	result = {}

	# for each column, look for an existing asset type, else make a new one
	column_num=1
	for column in header_row:
	    if column.startswith('@'):
		# this is a special field 
		result[column_num] = column

	    else:
		candidate_types = AssetType.objects.filter(name= column)
		if candidate_types.count() == 0:
		    # none found with this name.  make a new one.
		    asset = AssetType(name=column)	
		    asset.save()
		    print "Created new asset type %s" % asset
		else:
		    # use existing
		    asset = candidate_types[0]
		result[column_num] = asset
	    column_num += 1

	return result

    @staticmethod
    def find_or_create_lesson(lesson_name):
	lessons = Lesson.objects.filter(name = lesson_name)
	if lessons.count() == 0:
	    # none found with this name.  make a new one.
	    lesson = Lesson(name=lesson_name)	
	    lesson.save()
	    print "New lesson %s" % lesson
	    return lesson
	else:
	    # use existing
	    return lessons[0]


    # this method reads a CSV file as exported from hskflashcards
    @staticmethod
    def import_csv(filename):

	print "Reading from CSV file %s" % filename
	reader = csv.reader(open(filename))
	
	header_row = reader.next()
	asset_type_map = BulkCsv.asset_type_map_from_header_row(header_row)

	for csvrow in reader:
	    # csv module doesn't deal well with unicode input, so I convert it by hand
	    unicoderow = []
	    for item in csvrow:
	       unicoderow.append( unicode( item, 'utf-8' ))
	    # TODO: make this more general
	    concept_name = "%s / %s / %s" % ( unicoderow[5],unicoderow[3],unicoderow[4])
	    concept = Concept()
	    concept.description = concept_name
	    concept.save()

	    column_num = 1
	    for item in unicoderow:
		column_type = asset_type_map[column_num]
		if isinstance(column_type,AssetType):
		    asset = Asset()
		    asset.concept = concept
		    asset.content = item
		    asset.asset_type = column_type
		    asset.save()
		else:
		    if column_type == "@Lesson":
			# search for or create a lesson object
			lesson = BulkCsv.find_or_create_lesson(item)
			lesson_seq = LessonSequence(lesson=lesson, concept=concept)
			#lesson_seq.concepts.add(concept) # doesn't work with intermediate model
			lesson_seq.save()
			#print "Created lesson seq %s" % lesson_seq

		    if column_type == "@Sequence":
			# assuming this concept only has one lesson associated 
			# with it since we're in creation mode.
			lesson_seq = LessonSequence.objects.filter(concept = concept, lesson = lesson)[0]
			#print u"setting lessonseq %s" % lesson_seq
			#print lesson_seq
			lesson_seq.sequence = item
			lesson_seq.save()
			#print u"did-set lessonseq %s to %s" % (lesson_seq, item)
		    
		column_num += 1

	    print "Created %s" % concept

	
def main():
    setup_environ(settings)
    BulkCsv.import_csv( sys.argv[1] )

if __name__ == "__main__":
    main()
