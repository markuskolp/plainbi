export const extractResponseData = (res) =>
  res.data.length === 0 || res.data.length === undefined ? res.data.data : res.data;

export const sortByName = (data) =>
  [...data].sort((a, b) => {
    const nameA = a.name.toUpperCase();
    const nameB = b.name.toUpperCase();
    if (nameA < nameB) return -1;
    if (nameA > nameB) return 1;
    return 0;
  });
