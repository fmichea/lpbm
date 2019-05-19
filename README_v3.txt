  - All models saved to file are uniquely identified using a UUID.
  - Model names must be unique.
  - All models are validated with a schema.

Model Reference
---------------

The Model Reference is a special schema type that can be used to manage
external references to other model instances.

The Model Session
-----------------

The goal of the model session is to ensure that all actions made on the blog
data can easily be committed to disk all at once. It reduces the risk of
leaving the blog's data in a bad state in case of failure.
