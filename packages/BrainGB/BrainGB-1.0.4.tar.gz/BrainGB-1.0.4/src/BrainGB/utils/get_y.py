from torch_geometric.data import Data


def get_y(dataset: [Data]):
    """
    Get the y values from a list of Data objects.
    """
    y = []
    for d in dataset:
        y.append(d.y.item())
    return y


def get_site(dataset: [Data]):
    """
    Get the site values from a list of Data objects.
    """
    site = []
    for d in dataset:
        site.append(d.site)
    return site
