Pure Storage Access
===================

We need secrets to make API call.

.. code-block::


       {
       "client_id": "25********************************0d",
       "key_id": "f**************************************d",
       "client_name": "apitest",
       "storage": "purestorage.cam.ac.uk",
       "user": "pureuser",
       "password": "********,
       "keyfile": "/tmp/fa2xprivate.pem"
       }



To generate necessay field mentioned above, we need to create user and API client.

STEP 1. Login to Pure storage URL > settings

.. image:: access1.jpg
   :target: access1.jpg
   :alt: Pure Storage Access1

STEP 2. Click on the "Access" tab

.. image:: access2.jpg
   :target: access2.jpg
   :alt: Pure Storage Access2

STEP 3. Click on the dots of User table and click create User

.. image:: access3.jpg
   :target: access3.jpg
   :alt: Pure Storage Access3

STEP 4. Input the required fields and create with role "Array Admin".

This inputs will be utilized in secrets.json
    "user": "****",
    "password": "********,

.. image:: access4.jpg
   :target: access4.jpg
   :alt: Pure Storage Access4

STEP 5. Click on the dots to create the API clients

.. image:: access5.jpg
   :target: access5.jpg
   :alt: Pure Storage Access5

STEP 6. Input the necessay field with role "Array Admin".

This inputs will be utilized in secrets.json
    "client_id": "25********************************0d",
    "key_id": "f**************************************d",
    "client_name": "apitest",

.. image:: access6.jpg
   :target: access6.jpg
   :alt: Pure Storage Access6


NOTE: In the step6, public key must be added and private key will be utilized to make API Calls
    "keyfile": "/tmp/fa2xprivate.pem"
