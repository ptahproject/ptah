==================
Database Structure
==================

If you add Ptah to your project there are some database schema requirements.  You name your tables whatever you like.

ptah_blobs
----------
This table provides the ability to support large binary objects.  It is used by the :py:class:`ptah.cms.blob.Blob` model.  

+----------+---------+-------+---------+----------------------+
| Name     | Type    | Null  | Default | Comments             |
+==========+=========+=======+=========+======================+
| id       | int     | False | ''      | PK, FK ptah_nodes.id |
+----------+---------+-------+---------+----------------------+
| mimetype | varchar | True  | ''      |                      |
+----------+---------+-------+---------+----------------------+
| filename | varchar | True  | ''      |                      |
+----------+---------+-------+---------+----------------------+
| size     | int     | True  | 0       |                      |
+----------+---------+-------+---------+----------------------+
| data     | blob    | True  |         |                      |
+----------+---------+-------+---------+----------------------+

ptah_content
------------
The `ptah_content` table provides a definition for base content model.  It is used by the :py:class:`ptah.cms.Content` model.

+--------------+----------+-------+---------+----------------------+
| Name         | Type     | Null  | Default | Comments             |
+==============+==========+=======+=========+======================+
| id           | int      | False | ''      | PK, FK ptah_nodes.id |
+--------------+----------+-------+---------+----------------------+
| path         | varchar  | True  |         |                      |
+--------------+----------+-------+---------+----------------------+
| name         | varchar  | True  |         | Maxlength 255        |
+--------------+----------+-------+---------+----------------------+
| title        | varchar  | True  |         |                      |
+--------------+----------+-------+---------+----------------------+
| description  | varchar  | True  |         |                      |
+--------------+----------+-------+---------+----------------------+
| created      | datetime | True  |         |                      |
+--------------+----------+-------+---------+----------------------+
| modified     | datetime | True  |         |                      |
+--------------+----------+-------+---------+----------------------+
| effective    | datetime | True  |         |                      |
+--------------+----------+-------+---------+----------------------+
| expires      | datetime | True  |         |                      |
+--------------+----------+-------+---------+----------------------+
| lang         | varchar  | True  |         |                      |
+--------------+----------+-------+---------+----------------------+


ptah_nodes
----------
The `ptah_nodes` table provides the base model for all data elements in the system.  This table is used by the :py:class:`ptah.cms.Node` model.  

+-------------+----------+-------+---------+---------------------+
| Name        | Type     | Null  | Default | Comments            |
+=============+==========+=======+=========+=====================+
| id          | int      | False | ''      | Primary key         |
+-------------+----------+-------+---------+---------------------+
| type        | varchar  | True  | ''      |                     |
+-------------+----------+-------+---------+---------------------+
| uri         | varchar  | False |         | Maxlength=255       |
+-------------+----------+-------+---------+---------------------+
| parent      | varchar  | True  | ''      | FK: ptah_nodes.uri  |
+-------------+----------+-------+---------+---------------------+
| owner       | varchar  | True  | ''      | Principal URI       |
+-------------+----------+-------+---------+---------------------+
| roles       | text     | True  | '{}'    | JSON                |
+-------------+----------+-------+---------+---------------------+
| acls        | text     | True  | '[]'    | JSON                |
+-------------+----------+-------+---------+---------------------+
| annotations | varchar  | True  | '{}'    | JSON                |
+-------------+----------+-------+---------+---------------------+

ptah_settings
-------------
The `ptah_settings` table provides key, value for internal ptah settings machinery, in particular the :py:class:`ptah.settings.SettingRecord` model.  

+--------+---------+-------+---------+---------------------+
| Name   | Value   | Null  | Default | Comments            |
+========+=========+=======+=========+=====================+
| name   | varchar | False |         | Primary key         |
+--------+---------+-------+---------+---------------------+
| value  | varchar | True  | ''      |                     |
+--------+---------+-------+---------+---------------------+


ptah_tokens
-----------
The `ptah_tokens` table provides a space for transient tokens which are generated by application, such as password-reset tokens. You use the token service API but this table is used by :py:class:`ptah.token.Token` model table.

+-------+----------+-------+---------+---------------------+
| Name  | Value    | Null  | Default | Comments            |
+=======+==========+=======+=========+=====================+
| id    | int      | False |         | Primary key         |
+-------+----------+-------+---------+---------------------+
| token | varchar  | True  |         | MaxLegnth 48        |
+-------+----------+-------+---------+---------------------+
| valid | datetime | True  |         |                     |
+-------+----------+-------+---------+---------------------+
| data  | varchar  | True  |         |                     |
+-------+----------+-------+---------+---------------------+
| type  | varchar  | True  |         | MaxLength 48        |
+-------+----------+-------+---------+---------------------+

ptah_db_versions
----------------
The `ptah_db_versions` table contains migration revisions information.

+-------------+----------+-------+---------+---------------------+
| Name        | Value    | Null  | Default | Comments            |
+=============+==========+=======+=========+=====================+
| package     | str      | False |         | Primary key         |
+-------------+----------+-------+---------+---------------------+
| version_num | varchar  | True  |         | MaxLegnth 32        |
+-------------+----------+-------+---------+---------------------+
