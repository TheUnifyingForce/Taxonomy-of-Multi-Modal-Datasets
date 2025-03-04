# Taxonomy-of-Multi-Modal-Datasets
Master Project_UZH

## Kick-off
The goal of this Master project is to develope a systematic framework to extract semantic relationships between modalities (e.g., images, text) and their associated data types (e.g., JPEG, CSV) from the information of dataset metadata. By constructing a knowledge graph that formalizes these relationships, we aim to enable structured taxonomy and efficient search capabilities for multimodal dataset.

## **Repository Structure**  
- 📂 **01 Dataset Selection** – Chapter 2
- 📂 **02 Model Selection** – Chapter 3
- 📂 **03 Data Types Extraction** – Chapter 4
- 📂 **04 Normalization of Multimodal Data Representation** – Chapter 5
- 📂 **05 Knowledge Graph Construction** – Chapter 7
- 📜 **README.md** – Project documentation  

## Usage
1. To apply this to your own data, simply run the relevant notebooks or scripts in each folder as needed.
2. To explore our Knowledge Graph, refer to the examples below.

## Knowledge Graph Application
1. Name Space

```
prefix mp: <http://masterproject.org/> 
prefix ns1: <https://www.wikidata.org/wiki/> 
prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> 
prefix wd: <http://www.wikidata.org/entity/> 
prefix xsd: <http://www.w3.org/2001/XMLSchema#> 
```

2. Example 1

Select datasets which has Modality 'text' and Datatype 'sentence pair'

```
SELECT distinct ?Datasetlabel ?DatasetDesc WHERE {
        ?Dataset rdfs:label ?Datasetlabel .
    	?Dataset mp:dataset_description ?DatasetDesc .
        ?Dataset mp:Dataset_Modality ?modality .
        ?modality rdfs:label "text"  .
    	?Dataset mp:Dataset_Datatype ?datatype .
    	?datatype rdfs:label "sentence pair"     
        }
limit 5
```

3. Example 2

Select Datatype which has same relationship with 'image' as 'logo image' and Datasets contain Modality 'image' and the new Datatype

```
SELECT ?Datatypelabel ?Datasetlabel
WHERE {
    	?Dataset mp:dataset_description ?DatasetDesc .
        ?Dataset mp:Dataset_Modality ?MDimage .
    	?Dataset mp:Dataset_Datatype ?Datatype . 
    
    	?Dataset rdfs:label ?Datasetlabel
{
SELECT distinct ?Datatype ?Datatypelabel ?MDimage WHERE {
    	?DTlogoimage rdfs:label "logo image" .
    	?MDimage rdfs:label "image" .
        ?DTlogoimage ?p ?MDimage .
    
    	?Datatype ?p ?MDimage .
   		?Datatype rdfs:label ?Datatypelabel  .  
        }
limit 1
}
}limit 5
```