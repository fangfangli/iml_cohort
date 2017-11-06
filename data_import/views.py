# -*- coding: utf-8 -*-
from django.shortcuts import render
from django.conf import settings
from django.core.files.storage import FileSystemStorage
import numpy as np

# from .models import Document 
from .forms import DocumentForm
import pandas as pd
import os
import shutil
from scipy import sparse, io


file_upload_dir = os.path.join(settings.BASE_DIR, 'data')
fs = FileSystemStorage(location=file_upload_dir)


def handle_uploaded_file(f):
    features=pd.read_csv(f,nrows=1)
    return features

#accept the file, process it and store it locally in csv format
def process_file(f,new_features):
    doc = pd.read_csv(f)
    new_doc = doc[new_features]
    distinct_dias = new_doc.ICD9_CODE.unique()
    distinct_pates = new_doc.SUBJECT_ID.unique()
    diags = []
    data = []
    for p in distinct_pates:
        #print p
        vec = np.zeros(len(distinct_dias),dtype=int)
        ps = new_doc[new_doc['SUBJECT_ID']==p]
        str_diags = '\t'.join(ps.ICD9_CODE)
        for code in ps.ICD9_CODE:
            index = distinct_dias.tolist().index(code)
            vec[index] += 1
        data.append(vec)
        diags.append(str_diags)
        
    sparse_data = sparse.csr_matrix(data)

    file_path_data = os.path.join(settings.BASE_DIR, 'data/outcome_data')
    file_path_pationid = os.path.join(settings.BASE_DIR, 'data/outcome_pation.csv')
    file_path_deid = os.path.join(settings.BASE_DIR, 'data/outcome_deid.csv')
    file_path_diags = os.path.join(settings.BASE_DIR, 'data/outcome_diags.csv')

#     new_data = pd.DataFrame(data)
    distinct_dias_data = pd.DataFrame(distinct_dias)
    distinct_pates_data = pd.DataFrame(distinct_pates)
     
    #newm = io.mmread(file)
    io.mmwrite(file_path_data, sparse_data)
    distinct_dias_data.to_csv(file_path_deid,header=False)
    distinct_pates_data.to_csv(file_path_pationid,header=False)
    pd.DataFrame(data=diags,columns=['diags']).to_csv(file_path_diags)



def renew(request):
    if request.method == 'POST':
        new_features = request.POST.getlist('new_features')
        file_path = os.path.join(settings.BASE_DIR, 'tmp/tmp.csv')
        process_file(file_path,new_features)
        content = {'Title': "Feature Processing - Cohort Discovery Tool",
                   "listId":"li3",
                   'features': new_features} 
        return render(
            request,
            'data_import/stp3-fea-processing.html',
            content
        )


def list(request):
    # Handle file upload
    if request.method == 'POST':
        form = DocumentForm(request.POST, request.FILES)
        if form.is_valid():
            print "request files in list-----",request.FILES
            docfile = request.FILES['docfile']
            features = handle_uploaded_file(docfile)
            file_upload_dir = os.path.join(settings.BASE_DIR, 'tmp')
            fs = FileSystemStorage(location=file_upload_dir)
            if os.path.exists(file_upload_dir): 
                shutil.rmtree(file_upload_dir)
            fs.save("tmp.csv", docfile)
            
            content = {'Title': "Feature Selection - Cohort Discovery Tool",
                   "listId":"li2",
                   'features': features} 
            return render(
                request,
                'data_import/stp2-fea-selection.html',
                content
            )

    else:
        content = {'Title': "Upload Data - Cohort Discovery Tool",
                   "listId":"li1"}    
        return render(request, 'data_import/stp1-import.html', content)
