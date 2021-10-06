# Database Schema

## Tables

- PK: primary key
- FK: foreign key
- UK: unique
- NU: not null

### account

a account table that contain bot/team or user account information.

| Column Name                | Data Type | Key Type | Not Null | Description                                                                  |
|----------------------------|-----------|----------|----------|------------------------------------------------------------------------------|
| id                         | int       | UK       |          | a unique id for the account, this key currently only use for this table.     |
| email                      | char      | PK       | Yes      | a unique email in this table. We use email as a unique user                  |
| chinese_name               | varchar   |          |          | a chinese name representative                                                |
| first_name                 | varchar   |          | Yes      | a prefer english first name                                                  |
| last_name                  | varchar   |          | Yes      | a english last name                                                          |
| nickname                   | varchar   |          |          | some other name want people to call a user                                   |
| phone_number               | varchar   |          |          | contact phone number                                                         |
| shirt_size                 | varchar   |          |          | shirt size. Such XS, X, M, ...etc                                            |
| company                    | varchar   |          |          | current working company                                                      |
| school                     | varchar   |          |          | current school or graduated school                                           |
| register_date              | datetime  |          |          | a account register account date. ISO time format                             |
| dietary_restriction        | varchar   |          |          | a account dietary restriction                                                |
| reimbursement_platform     | varchar   |          |          | a account reimbursement platform, such as Paypal, or Zelle                   |
| reimbursement_method       | varchar   |          |          | reimbursement method, such as phone, or email                                |
| reimbursement_phone_number | varchar   |          |          | reimbursement phone number                                                   |
| reimbursement_email        | varchar   |          |          | reimbursement email                                                          |
| join_date                  | datetime  |          |          | a account user/bot join to organization date. ISO time format                |
| birthday                   | datetime  |          |          | a account user/bot birthday. ISO time format                                 |
| memo                       | jsonb     |          |          | a note for user                                                              |
| type                       | varchar   |          |          | a account type, can be user or bot/team                                      |
| review_by_id               | varchar   | FK       |          | the account has been review by whom. contain ZgID                            |
| review_status              | varchar   |          |          | a review status, such as pending, approved, or deny                          |
| has_iam_google_account     | boolean   |          |          | Does the user has google workspace account?                                  |

### group

a group may link to the google workspace group by google group email(mailing list)

| Column Name  | Data Type | Key Type | Not Null | Description                                                                         |
|--------------|-----------|----------|----------|-------------------------------------------------------------------------------------|
| id           | int       | PK       | Yes      | a unique id for a group, this key currently only use for this table. Auto-increment |
| year         | int       |          |          | a year this group belong to                                                         |
| session      | int       |          |          | a session for this group belong to corresponding to year                            |
| chinese_name | varchar   |          |          | chinese name for group                                                              |
| english_name | varchar   |          |          | english name for group                                                              |
| email        | varchar   | UK       |          | a unique email for this group corresponding to google group                         |
| memo         | jsonb     |          |          | notes for this group                                                                |

### user_group

A many to many user group mapping table

| Column Name | Data Type | Key Type | Not Null | Description |
|-------------|-----------|----------|----------|-------------|
| user_id     | varchar   | PK, FK   | Yes      | a account id|
| group_id    | int       | PK, FK   | Yes      | a group id  |

## ER Diagram

![Schema](./schema.png)

## Reference

- table generate by [tableconvert](tableconvert.com)
- backup ER Diagram [LINK](https://lucid.app/publicSegments/view/65035835-c23a-47bd-bfc3-4e604ba177b4/image.png)
- LuciaChart [LINK](https://lucid.app/lucidchart/75c8eca5-2dcb-4634-a830-23de4aadd7fe/edit)
