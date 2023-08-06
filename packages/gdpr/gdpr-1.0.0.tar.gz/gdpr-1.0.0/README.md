# Publish to PyPI, and let's see how the *Python Software Foundation* interprets consent GDPR-wise

## Context
[*PyPI was subpoenaed*](https://blog.pypi.org/posts/2023-05-24-pypi-was-subpoenaed/), especially [*point 6*](https://blog.pypi.org/posts/2023-05-24-pypi-was-subpoenaed/#6-telephone-or-instrument-numbers-including-the-registration-internet-protocol-address):

> A synopsis of all IP Addresses for each username from previous records were shared. These were sourced from our database records and are private to PyPI.

* [*Hacker News* discussion about this](https://news.ycombinator.com/item?id=36061407)
* [*Who does the data protection law apply to?*](https://commission.europa.eu/law/law-topic/data-protection/reform/rules-business-and-organisations/application-regulation/who-does-data-protection-law-apply_en)
* [*Does the GDPR apply to companies outside of the EU?*](https://gdpr.eu/companies-outside-of-europe/)
* [*When do the GDPR provisions apply to non-EU businesses?*](https://www.activemind.legal/guides/gdpr-non-eu-businesses/)

## Steps to reproduce
* Be in the European Union. No citizenship required.
* Create an account at https://pypi.org/account/register/ ([*archive.is* English localization memento from 24 May 2023 20:25:43 UTC](https://archive.is/CdDOa)). Notice that you don't have to provide any explicit consent to any terms and conditions.
* Confirm verification e-mail. Notice it just contains a confirmation link, e.g. `https://pypi.org/account/verify-email/?token=eyJhY3Rpb24iOiJlbWFpbC12ZXJpZnkiLCJlbWFpbC5pZCI6IjEyMzQ1IiwiYWxnIjoiSFMyNTYifQ.YWJjZA.bB3cVvD2EnTZ7sOD7XNPnxv0xgl9Q3svmcDCG8UTR9Q`.
  * The *token* parameter value is an unencrypted, *HMACSHA256*-signed *JSON Web Token*, in this example it provides the following information (try it out at https://jwt.io/):
```
// header
{
  "action": "email-verify",
  "email.id": "12345",
  "alg": "HS256"
}

// payload
"abcd"
```
* Visit the [*Python Packaging Authority*'s (PyPA) *pypa/sampleproject* GitHub project page](https://github.com/pypa/sampleproject).
* Select *Use this template* and create your own fork, e.g. [*Abdull/gdpr*](https://github.com/Abdull/gdpr).
* Adapt repository files, in particular *pyproject.toml* and *README.md*.
* Build:
```
# see https://packaging.python.org/en/latest/flow/
# see https://packaging.python.org/en/latest/tutorials/installing-packages/
# see https://packaging.python.org/en/latest/tutorials/packaging-projects/

# assuming Debian 11 bullseye in the following

# get ensurepip, Debian apt-way:
sudo apt install python3-venv

pip install --upgrade pip setuptools wheel build

# inside your project
python3 -m build

# on success, shall end with line
# Successfully built gdpr-1.0.0.tar.gz and gdpr-1.0.0-py3-none-any.whl

```
