# Deploying and Configuring OpenLDAP Directory Service

Deploy & configure guide for OpenLDAP Directory Service on Debian. Many things was getted from [this](https://www.zytrax.com/books/ldap/) beautiful site, based on [this](https://www.openldap.org/software/repo.html) quick-start official guide. See [Useful Links](#useful_links) section below for more info from there.

## Table of Contents

* [Preamble](#Preamble)
* [Pre-requirements](#Pre-requirements)
* [Tested on](#tested_on)
* [Step by step guide](#step_by_step_guide)
    * [A. Prepraing OS before OpenLDAP Installation](#a)
    * [B. Downloading and Installing slapd](#b)
    * [C. Configuring slapd](#c)
    * [D. Launching slapd](#d)
    * [E. Adding data to DS](#e)
* [Troubleshooting](#Troubleshooting)
* [Useful Links](#useful_links)

## Preamble

If you having issues with downloading materials used in this instruction, check the `/assets` folder. I tried to save everything that I use in there.  
**IMPORANT**: Be very careful with whitespaces and newlines! LDIF very sensitive to them

## Pre-requirements

* Be familiar with basic LDAP concepts. [This](https://www.zytrax.com/books/ldap/ch1/#how) guide is very good point to start from.
* (Optional) Your own LDIF's with schemas and data if needed. Copy them to the server in any folder

## Tested on<a name="tested_on"></a>

* Debian 11
* OpenLDAP 2.5.19

## Step by step guide<a name="step_by_step_guide"></a>

### A. Prepraing OS before OpenLDAP Installation<a name="a"></a>

1. Install dev versions of required libraries to support SASL and TLS: 
    ```bash
    sudo apt install libssl-dev libsasl2-dev
    ```

### B. Downloading and Installing slapd<a name="b"></a>

1. Download OpenLDAP from [official source](https://www.openldap.org/software/download/). You're loking for [2.5.19 LTS version](https://www.openldap.org/software/download/OpenLDAP/openldap-release/openldap-2.5.19.tgz).

2. Now we starting to follow oficial [quick-start guide](https://openldap.org/doc/admin25/quickstart.html) from OpenLDAP site from point **2** to **7** with some small changes:

    1. Go to folder with downloaded OpenLDAP
    2. Extract it:
        ```bash 
        gunzip -c openldap-2.5.19.tgz | tar xvfB -
        ```
    3. Go to extracted folder: 
        ```bash
        cd openldap-2.5.19
        ```
    4. Run configure: 
        ```bash
        ./configure --with-cyrus-sasl --with-tls
        ```
        * **IMPORTANT:** SASL and TLS support is configured by default if you have all necessary libraries. These keys are used as explicit mark for that functionality. Check the `configure` output for the approvement of right configuration.  
        Example of right configuration for TLS:
            ```bash
            checking openssl/ssl.h usability... yes
            checking openssl/ssl.h presence... yes
            checking for openssl/ssl.h... yes
            checking for SSL_CTX_set_ciphersuites in -lssl... yes
            ```
            And for SASL:
            ```bash
            checking sasl/sasl.h usability... yes
            checking sasl/sasl.h presence... yes
            checking for sasl/sasl.h... yes
            checking sasl.h usability... no
            checking sasl.h presence... no
            checking for sasl.h... no
            checking for sasl_client_init in -lsasl2... yes
            checking for sasl_version... yes
            ```
    5. Make dependencies: 
        ```bash
        make depend
        ```
    6. Make OpenLDAP: 
        ```bash
        make
        ```
    7. (Optional) Run tests: 
        ```bash
        make test
        ``` 
        * **IMPORTANT:** You need at least 8GB of RAM to successfully run the tests. Other way process may just hang on while testing: I faced with this issue with 4GB of RAM.
    8. Installing OpenLDAP: 
        ```bash
        sudo make install
        ```

### C. Configuring slapd<a name="c"></a>

* *TODO: Change root to service user*

1. Create directories for configuration and database:
    ```bash
    sudo mkdir -p /usr/local/etc/slapd.d
    sudo mkdir -p /usr/local/var/openldap-data
    ```
2. Preraring `slapd.ldif`. Open template file at `/usr/local/etc/openldap/slapd.ldif` in your favorite editor and change it.

    1. Copy files from `/assets/2/ldifs/schema` to `/usr/local/etc/openldap/schema` on server.

    2. For the purpose of use `InetOrgPerson` objectClass (very popular objectClass to hold information about arbitrary user data), add these schemas inclusion right after line with `core` schema include:
    * **NOTE:** You can include your own custom schemas as well. For example, you can include schema `person_with_uuid.ldif` from `assets/2/ldifs/schemas`
    ```ldif
    # ...
    dn: cn=schema,cn=config
    objectClass: olcSchemaConfig
    cn: schema

    include: file:///usr/local/etc/openldap/schema/core.ldif
    # Place schemas below this line
    include: file:///usr/local/etc/openldap/schema/cosine.ldif
    include: file:///usr/local/etc/openldap/schema/nis.ldif
    include: file:///usr/local/etc/openldap/schema/inetorgperson.ldif
    # Custom schemas (you need to copy it to the server before include)
    include: file:///tmp/person_with_uuid.ldif
    # ...
    ```
    3. *TODO: olcAccess*
    4. Change `olcSuffix`, `olcRootDN` and `olcRootPW`:
        * **NOTE #1:** `olcSuffix` is used as a tree root for the data in your data catalogue. `olcRootDN` and `olcRootPW` - credentials for administrator account.
        * **NOTE #2:** `olcSuffix` for domain `a.b.c.d.org` is `dc=a,dc=b,dc=c,dc=d,dc=org`
        * **NOTE #3:** `olcRootDN` = `cn=Manager,` + `olcSuffix`. `cn` may be also replaced by your desire 
        * **IMPORTANT:** Do not forget to remove `olcRootDN` and `olcRootPW` from your configuration before production usage!
        ```ldif
        # ...
        olcSuffix: dc=book,dc=org
        olcRootDN: cn=Manager,dc=book,dc=org
        # ...
        olcRootPW: admin
        # ...
        ```
    5. (Optional) Add some indices if needed in order to dramatically improve search speed:
        * **IMPORTANT 1:** If you have at least 500000 users in your directory service (DS), searching one of them by filter with single equal condition field will take **minutes** without `eq` index. More about [indices](https://www.zytrax.com/books/ldap/ch6/#index)
        * **IMPORTANT 2:** `eq,sub` - right, `eq, sub` - wrong (will cause an error)
        ```ldif
        # ...
        # Indices to maintain
        olcDbIndex: objectClass eq
        # Place indices below this line
        olcDbIndex: uid eq
        olcDbIndex: sn eq,sub
        # ...
        ```
### D. Launching slapd<a name="d"></a>

1. Make initial applyment your configuration:
    ```bash
    sudo /usr/local/sbin/slapadd -n 0 -F /usr/local/etc/slapd.d -l /usr/local/etc/openldap/slapd.ldif
    ```
    * **IMPORTANT #1:** Right output of previus command is single line `Closing DB...`. Other way see [troubleshooting](#Troubleshooting) section.
    * **IMPORTANT #2:** You have only one chance to apply the configuration by the `slapadd` command. If you get some errors, fix them, remove every single file from folder `/usr/local/etc/slapd.d` and only then try `slapadd` command again.
2. (Optional) Add admin credentials for `cn=config` entry. It'll allow you configure your OpenLDAP via GUI clients like [Apache Directory Studio](https://directory.apache.org/studio/).
    * **IMPORTANT:** Do not forget to remove `olcRootDN` and `olcRootPW` from your configuration before production usage!

    1. Create password:
    ```bash
    sudo slappasswd -h {MD5}
    ```
    2. Copy `/assets/2/ldifs/change_config_passwd.ldif` to any folder on the server and replace value of `olcRootPW` to created password on previous step:
    ```ldif
    # ...
    # Password: "admin"
    olcRootPW: {MD5}ISMvKXpXpadDiUoOSoAfww==
    # ...
    ```
    3. Apply created configuration:
    ```bash
    sudo /usr/local/sbin/slapmodify -n 0 -F /usr/local/etc/slapd.d -l change_config_passwd.ldif
    ```
    * **IMPORTANT:** You need to restart slapd if already runnig
    4. Now you can access your `cn=config` with following connection parameters after slapd will be launched:
    ```plain
    Bind DN or user: cn=admin,cn=config
    Password: admin
    Base DN: cn=config
    ```
3. Run the slapd:
    ```ldif
    sudo /usr/local/libexec/slapd -F /usr/local/etc/slapd.d
    ```
    * **NOTE:** To kill launched slapd instance use:
        ```bash
        sudo kill -9 $(cat /usr/local/var/run/slapd.pid)
        ```
4. Now you can manipulate data in your DS with following connection parameters:
    ```plain
    Bind DN or user: cn=Manager,dc=book,dc=org
    Password: admin
    Base DN: dc=book,dc=org
    ```
5. (Optional) You may also create a service for slapd:

    1. Copy `/assets/2/openldap.service` to `/etc/systemd/system/slapd.service` on the server
    2. Enable and run service:
        ```bash
        sudo systemctl enable slapd
        sudo systemctl start slapd
        ```

### E. Adding data to DS<a name="e"></a>

1. Copy `01.phonebook.ldif` and `02.people.ldif` from `/assets/2/ldifs` to any folder on the server.

2. Append LDIFs. Password: `admin`
```bash
ldapadd -H ldap://127.0.0.1 -x -W -D "cn=Manager,dc=book,dc=org" -f 01.phonebook.ldif
ldapadd -H ldap://127.0.0.1 -x -W -D "cn=Manager,dc=book,dc=org" -f 02.people.ldif
```

## Troubleshooting

1. slapadd errors 
    1. `str2entry: entry -1 has multiple DNs "<some schema cn>" and "olcDatabase=frontend,cn=config"`  
    **SOLUTION:** Add linebreak in the end of your schema

## Useful Links<a name="useful_links"></a>

- "LDAP for Rocket Scientists" (c):
    - [LDAP Therms Glossary](https://www.zytrax.com/books/ldap/apd/) - like CN, DN, SN, RDN, etc.
    - [Commonly Used Attributes](https://www.zytrax.com/books/ldap/ape/)
    - [Configuration Attributes and Directives](https://www.zytrax.com/books/ldap/ch6/#list) - slapd.conf | cn=config
- [OpenLDAP 2.5 Quick-Start Guide](https://openldap.org/doc/admin25/quickstart.html)
- [OpenLDAP Source Repositories](https://www.openldap.org/software/repo.html)