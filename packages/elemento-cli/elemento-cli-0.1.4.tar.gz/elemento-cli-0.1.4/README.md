<br/>
<br/>
<br/>
<img src="https://raw.githubusercontent.com/Elemento-Modular-Cloud/graphic-assets/main/logos/horizontal/Logo%20horizontal%20lightbg%20transp.svg" width=50%/>
<br/>

# Elemento command line overview

###### tags: `elemento` `CLI` `tech` `CTO` `tutorials`

<style>
    h1, h2, h3, h4, h5, h6, h7, p, a {
        font-family: Arial, Helvetica, sans-serif;
    }
</style>


# Elemento command line overview

## Authentication
Before using the Elemento CLI you would need to **authenticate**!

`elemento auth login`

Do you have an **account**? No, [create yours here](https://elemento.typeform.com/to/p3zAUodM)

**Forgot** your password? [Recover it here](https://portal.elemento.cloud/api/v1/user/recovery)

`elemento auth logout`

## Info about daemons

`elemento info` will tell you if the daemons are running properly.

It is possible to get the client daemons from
- Mac https://repo.elemento.cloud/app/Elemento_daemons.dmg
- Windows https://repo.elemento.cloud/app/Elemento_daemons.zip
- Linux https://github.com/Elemento-Modular-Cloud/electros

## Account Management

To use AtomOS you will need a License: [buy yours here](https://elemento.typeform.com/to/rUaZRm2O)!

From the CLI you can **list** your licenses

`elemento account list_licenses`

or **activate** one. AtomOS licenses become active and ready when you activate them, not when you buy them.

`elemento account activate_license --key `

the CLI will download your license and you'll find a *atomos.license* file:
- **keep it in a safe place!**
- copy it in */etc/elemento/atomos.license* path of your server (one license per server)
- restart the *elementolicensing* service `systemctl restart elementolicensing`

## Volumes

You can **list** your volumes.

`elemento volume list`

:::spoiler Pro Tip
Volumes will be searched in `/mnt/elemento-vault`, mount here your volumes!
:::

If you have not any volume you can ask if there is any server ready to create one for you

`elemento volume cancreate --size 1`

and then **create** or even **destroy** your volumes

`elemento volume create --size 1`

(Read our [tech pack](https://hackmd.io/REBdz_zXT9Koqcel-LbBJg) for a complete list of volume specification)

`elemento volume destroy fffffffffffffffffffffffffffffffff`

## Virtual Machines

You can manage your own volumes or **download** a standard *iso* image
`elemento vm getiso`

:::spoiler *iso* files
This command will download a file calles {os_flavour}.iso in /tmp and you can run vmw from this if using the Live image!
:::

then you can create your machine

`elemento vm create --spec-json /path/to/request.json --volumes-json /path/to/volumes.json`

(Read our [tech pack](https://hackmd.io/REBdz_zXT9Koqcel-LbBJg) for a complete list of volume specification)

## Templates
List some machines templates
`elemento vm gettemplates`

**List** your vms

`elemento vm list`

you will notice a SW and a HW link in the form *https://localhost:8443/#/clients/...* these will open a screen to manage your machines directly form your browser.
In order to use the software link you need to enable VNC (on Linux) or RDP (on Windows) with an account *elemento*.

or **destroy** them

`elemento vm destroy fffffffffffffffffffffffffffffffff`


## Community Edition
If you are interacting with servers running the *Community Edition* they will not be automacically discovered.

:::success
Before running the daemons put your server IP in `$HOME/.elemento/hosts`
:::

# AtomOS - server side

# Services

## Resource matcher server

`sudo systemctl status matcherserver`

## Storage server

`sudo systemctl status storageserver`

### Elemento paths

The **storageserver** searches Elemento volumes (*.elimg*) in */mnt*.

Add a new drive
- mount the drive in */mnt*
- add a *settings.json* in the new path specifing the number of VM volumes and their total size (in GB) as follows

```
{
    "max-volumes": 1,
    "max-size": 1000
}
```

Example of configuration

```
|/mnt
|/mnt/elemento-vault
|/mnt/elemento-vault/settings.json
```

## Licensing

First of all grab your [license](https://elemento.typeform.com/to/rUaZRm2O), activate it with the command line


`elemento account activate_license --key `

the CLI will download your license and you'll find a *atomos.license* file:
- **keep it in a safe place!**
- copy it in */etc/elemento/atomos.license* path of your server (one license per server)
- restart the *elementolicensing* service `systemctl restart elementolicensing`

Check the status of your service `sudo systemctl status elementolicensing`


# Doubts? Need help?

Open an *issue* in our [helpcenter](https://github.com/Elemento-Modular-Cloud/helpcenter)
