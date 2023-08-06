To generate schema following commands should be run:

1. Get introspection (you can also get it from gitlab introspection job artifacts)
```bash
python3 -m sgqlc.introspection --exclude-deprecated -H "Authorization: Bearer <token>" <graphql url> introspection.json
```
**Note**: for now there is some bug in sgqlc, so we should change default value 
`"{performSynchronously:true}"` to `null` for correct schema generation
2. Generate code
2.1. Generate code for api_schema
```bash
sgqlc-codegen schema introspection.json api_schema.py
```
2.2. Generate code for crawlers_api_schema
```bash
sgqlc-codegen schema introspection.json crawlers_api_schema.py
```
**Note**: in paginationVersionsCrawler we must change filter_settings default value to default value in introspection(for now it's False)
2.3. Generate code for utils_api_schema
```bash
sgqlc-codegen schema introspection.json utils_api_schema.py
```
2.4. Generate code for tcontroller_api_schema
```bash
sgqlc-codegen schema introspection.json tcontroller_api_schema.py
```
3. do not forget to comment/remove `import sgqlc.types.datetime` in `api_schema.py` and `utils_api_schema.py`.
4. add all `*api_schema.py` files to commit
