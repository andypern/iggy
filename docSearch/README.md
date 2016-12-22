
# mapper-attachments / tika:

our current rev:
https://www.elastic.co/guide/en/elasticsearch/plugins/2.3/mapper-attachments.html

latest:
https://www.elastic.co/guide/en/elasticsearch/plugins/5.x/mapper-attachments.html


To install:
		sudo bin/plugin install mapper-attachments

On 5.1, the new version is the 'ingest attachment' plugin, although it is different in nature..need to do more research

after installing must restart ES on all nodes.


Formats:

http://tika.apache.org/1.14/formats.html


## setup


simple as:

```
PUT docindex
{
  "mappings": {
    "doc": {
      "properties": {
        "file": { "type": "attachment" }
}}}}


```





## highlighting

https://www.elastic.co/guide/en/elasticsearch/plugins/5.x/mapper-attachments-highlighting.html


```

PUT /docindex

PUT /docindex/doc/_mapping
{
  "doc": {
    "properties": {
      "file": {
        "type": "attachment",
        "fields": {
          "content": {
            "type": "text",
            "term_vector":"with_positions_offsets",
            "store": true
          }
        }
      }
    }
  }
}
```
(in 5.x replace `string` with `text`)
shove a document in (base64 encoded string):
```
PUT /docindex/doc/1?refresh=true
{
  "file": "IkdvZCBTYXZlIHRoZSBRdWVlbiIgKGFsdGVybmF0aXZlbHkgIkdvZCBTYXZlIHRoZSBLaW5nIg=="
}
```
search :
```
GET /docindex/doc/_search
{
  "stored_fields": [],
  "query": {
    "match": {
      "file.content": "king queen"
    }
  },
  "highlight": {
    "fields": {
      "file.content": {
      }
    }
  }
}
```


Response looks similar to:

```
{
  "took": 25,
  "timed_out": false,
  "_shards": {
    "total": 5,
    "successful": 5,
    "failed": 0
  },
  "hits": {
    "total": 1,
    "max_score": 0.13561106,
    "hits": [
      {
        "_index": "docindex",
        "_type": "doc",
        "_id": "1",
        "_score": 0.13561106,
        "highlight": {
          "file.content": [
            "\"God Save the <em>Queen</em>\" (alternatively \"God Save the <em>King</em>\"\n"
          ]
        }
      }
    ]
  }
```
