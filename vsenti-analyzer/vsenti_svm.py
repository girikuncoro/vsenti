# vSenti SVM for sentiment classification
# Thanks to bayu@salestock for teaching me this through github.com/pyk/rojak project

# References:
# * Thumbs up? Sentiment Classification using Machine Learning Techniques
#   http://www.cs.cornell.edu/home/llee/papers/sentiment.pdf
# * Fast and accurate sentiment classification using an enhanced Naive Bayes
#   model
#   https://arxiv.org/pdf/1305.6143.pdf
# * Exploring Sentiment Classification Techniques in News Articles
#   http://researchdatabase.ac.zw/519/2/Exploring%20Sentiment%20Classification%20Techniques%20in%20News%20Articles.pdf
import csv
import sys
import re
import pickle
import itertools

from bs4 import BeautifulSoup
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.multiclass import OneVsRestClassifier
from sklearn.svm import LinearSVC
from sklearn import metrics
import matplotlib
matplotlib.use('Agg')
from matplotlib import pyplot
import numpy as np

# Compile regex to remove non-alphanum char
nonalpha = re.compile('[^a-z\-]+')

# Normalize the word
def normalize_word(w):
    word = w.lower()
    word = nonalpha.sub(' ', word)
    word = word.replace('-', ' ')
    word = word.strip()
    return word

# Function to clean the raw string
# TODO: remove stopwords
def clean_string(s):
    result_str = []

    # For each word we clear out the extra format
    for w in s.split(' '):
        word = normalize_word(w)
        if word != '' and word != '-':
            result_str.append(word)

    return ' '.join(result_str)

# Given list of article texts, this function will return a sparse matrix
# feature X
def extract_features(article, vocabulary=None, method='tf'):
    # We use {uni,bi,tri}gram as feature here
    # The feature should appear in at least in 3 docs
    vectorizer = CountVectorizer(ngram_range=(1,3),
        vocabulary=vocabulary, decode_error='ignore',
        min_df=3).fit(article)
    X = vectorizer.transform(article)
    if method == 'tfidf':
        X = TfidfTransformer().fit_transform(X)
    return X, vectorizer.get_feature_names()

# Plot confusion matrix
def plot_confusion_matrix(cm, classes, normalize=False, title='',
        cmap=pyplot.cm.Blues, classifier_name=''):
    pyplot.close('all')
    pyplot.imshow(cm, interpolation='nearest', cmap=cmap)
    pyplot.title(title)
    pyplot.colorbar()
    tick_marks = np.arange(len(classes))
    pyplot.xticks(tick_marks, classes, rotation=45)
    pyplot.yticks(tick_marks, classes)

    if normalize:
        cm = cm.astype('float') / cm.sum(axis=1)[:, np.newaxis]

    thresh = cm.max() / 2.
    for i, j in itertools.product(range(cm.shape[0]), range(cm.shape[1])):
        pyplot.text(j, i, cm[i, j],
                 horizontalalignment="center",
                 color="white" if cm[i, j] > thresh else "black")

    pyplot.ylabel('True label')
    pyplot.xlabel('Predicted label' + '\n\n' + classifier_name)
    pyplot.tight_layout()
    full_title = title + ' ' + classifier_name
    file_name = '_'.join(full_title.lower().split(' '))
    pyplot.savefig(file_name + '.png')

class VsentiSVM():
    # Storing classifier
    classifiers = {}

    # Map of label name and the corresponding classifier ID
    classifier_label = {
        'pos_vsphere': 'classifier_vsphere',
        'neg_vsphere': 'classifier_vsphere',
        'pos_nsx': 'classifier_nsx',
        'neg_nsx': 'classifier_nsx',
        'pos_vsan': 'classifier_vsan',
        'neg_vsan': 'classifier_vsan',
        'oot': 'all_classifier'
    }

    # Map classifier ID and the training and test data
    training_data_text = {
        'classifier_vsphere': [],
        'classifier_nsx': [],
        'classifier_vsan': []
    }
    training_data_class = {
        'classifier_vsphere': [],
        'classifier_nsx': [],
        'classifier_vsan': []
    }
    test_data_text = {
        'classifier_vsphere': [],
        'classifier_nsx': [],
        'classifier_vsan': []
    }
    test_data_class = {
        'classifier_vsphere': [],
        'classifier_nsx': [],
        'classifier_vsan': []
    }

    # Collect the data from csv file
    def _collect_data_from_csv(self, input_file, container_text,
            container_class):
        # Read the input_file
        csv_file = open(input_file)
        csv_reader = csv.DictReader(csv_file)
        for row in csv_reader:
            # Get the data
            try:
                content = row['content']
                label = row['sentiment']
            except KeyError as err:
                print 'Cannot load csv:', err
                sys.exit()

            # Clean the string
            clean_content = clean_string(content).encode('utf-8',
                'ignore')
            clean_text = clean_content
            if not clean_text:
                continue
            print "clean content: ", clean_text

            # Collect the training data
            # Skip unknown label
            if not label in self.classifier_label:
                continue
            classifier_name = self.classifier_label[label]
            if classifier_name == 'all_classifier':
                for key in self.training_data_text:
                    container_text[key].append(clean_text)
                    container_class[key].append(label)
            else:
                container_text[classifier_name].append(
                    clean_text)
                container_class[classifier_name].append(label)
        csv_file.close()

    # input_file is a path to csv with the following headers:
    # 'title', 'raw_content' and 'labels'.
    # output_file is a path where the model written into
    def train(self, input_file, output_file):
        # Collect the training data
        self._collect_data_from_csv(input_file, self.training_data_text,
            self.training_data_class)

        print "training data: ", self.training_data_text

        # For each classifier, we extract the features and train the
        # classifier
        for key in self.training_data_text:
            article_texts = self.training_data_text[key]
            article_labels = self.training_data_class[key]

            # Create feature extractor
            feature_extractor = TfidfVectorizer(ngram_range=(1,3),
                decode_error='ignore', min_df=3)
            feature_extractor.fit(article_texts)

            # Extract the features
            X = feature_extractor.transform(article_texts)
            y = article_labels

            # Train the classifier
            classifier = OneVsRestClassifier(LinearSVC(random_state=0))
            classifier.fit(X, y)

            # Save the classifier
            self.classifiers[key] = {
                'classifier': classifier,
                'feature_extractor': feature_extractor
            }

        # Save the model as binary file
        pickle.dump(self.classifiers, open(output_file, 'w'),
            protocol=pickle.HIGHEST_PROTOCOL)

    def eval(self, model, test_data):
        # Load the model
        self.classifiers = pickle.load(open(model))

        # Collect the test data
        self._collect_data_from_csv(test_data, self.test_data_text,
            self.test_data_class)

        # We do the evaluation
        for key in self.test_data_text:
            article_texts = self.test_data_text[key]
            article_labels = self.test_data_class[key]
            classifier = self.classifiers[key]['classifier']
            feature_extractor = self.classifiers[key]['feature_extractor']

            # Extract the features
            X = feature_extractor.transform(article_texts)
            y_true = article_labels

            # Predict
            y_pred = classifier.predict(X)

            # Evaluate the score
            precision = metrics.precision_score(y_true, y_pred,
                average='micro')
            recall = metrics.recall_score(y_true, y_pred,
                average='micro')
            f1_score = 2*((precision*recall)/(precision+recall))
            print 'classifier:', key
            print 'precision:', precision
            print 'recall:', recall
            print 'f1:', f1_score

            # Create the confusion matrix visualization
            conf_matrix = metrics.confusion_matrix(y_true, y_pred)
            plot_confusion_matrix(conf_matrix,
                classes=classifier.classes_,
                title='Confusion matrix without normalization',
                classifier_name=key)

    def predict(self, article):
        result = []
        for key in self.classifiers:
            classifier = self.classifiers[key]['classifier']
            feature_extractor = self.classifiers[key]['feature_extractor']
            X = feature_extractor.transform(article)
            res = classifier.decision_function(X)
            result = result + zip(classifier.classes_, res[0])
        return result

if __name__ == '__main__':
    vsenti = VsentiSVM()
    vsenti.train('training_data.csv', 'vsenti_svm_model.bin')
    vsenti.eval('vsenti_svm_model.bin', 'test_data.csv')

    print '== Test'
    # test_comment_texts = ['''
    #     any news on this? i have the same problem that my network connections
    #     stops working in windows 2012R2 my setup is on a vcloud director 5.5.2
    #     with vsphere 5.5 i already deinstalled
    # ''']
    # test_comment_label = 'neg_vsphere'
    test_comment_texts = ['''
        Hi,  You can try deleting these objects by using
         /usr/lib/vmware/osfs/bin/objtool from ESXi shell.  Sample command :
         Check the obj_info from RVC before you delete these 6 objects to be sure.
    ''']
    test_comment_label = 'pos_vsan'
    prediction = vsenti.predict(test_comment_texts)
    print 'Text comment:'
    print test_comment_texts
    print 'True label:', test_comment_label
    print 'Prediction:', prediction
