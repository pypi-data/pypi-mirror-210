# monitored instances
try:
    from pandas import DataFrame
except ImportError:

    def DataFrame():
        return dict(_instances)


# sqlite
lamin_site_assets = "s3://lamin-site-assets/lamin-site-assets.lndb"
bionty_assets = "s3://bionty-assets/bionty-assets.lndb"
swarm_test = "s3://ln-swarm/ln-swarm.lndb"

# postgres
lamindata = "postgresql://batman:robin@35.222.187.204:5432/lamindata"


_instances = [
    (lamin_site_assets, "lnschema_core"),
    (bionty_assets, "lnschema_core"),
    (swarm_test, "lnschema_core"),
    (swarm_test, "lnschema_bionty"),
    (lamindata, "lnschema_core"),
    (lamindata, "lnschema_bionty"),
    (lamindata, "lnschema_lamin1"),
]

instances = DataFrame(_instances)
