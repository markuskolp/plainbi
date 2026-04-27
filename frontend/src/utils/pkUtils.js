const ToBinary = (str) => {
  let result = "";
  str = encodeURIComponent(str);
  for (let i = 0; i < str.length; i++)
    if (str[i] == "%") { result += String.fromCharCode(parseInt(str.substring(i + 1, i + 3), 16)); i += 2; }
    else result += str[i];
  return result;
};

export const base64UrlSafeEncode = (input, isRepo) => {
  if (isRepo === 'true') return input;
  let base64 = btoa(ToBinary(input));
  return "[base64@" + base64.replace(/\+/g, '-').replace(/\//g, '_').replace(/=+$/, '') + "]";
};

export const getPKForURL = (record, pkColumn, isRepo) => {
  if (pkColumn.length <= 1) return base64UrlSafeEncode(record[pkColumn[0]], isRepo);
  let pkforurl = "(";
  for (let i = 0; i < pkColumn.length; i++)
    pkforurl += pkColumn[i] + ":" + base64UrlSafeEncode(record[pkColumn[i]], isRepo) + ":";
  return pkforurl.replace(/^:+|:+$/g, '') + ")";
};

export const getPKParamForURL = (pkColumn) => {
  if (pkColumn.length <= 1) return pkColumn[0];
  return pkColumn.join(",");
};

export const getColsParamForURL = (cols, pkColumns) => {
  const pkExists = (value) => pkColumns.some((col) => col.toLowerCase() === value.toLowerCase());
  return cols
    .filter((col) => !(col.showdetailsonly == 'true' && !pkExists(col.column_name)))
    .map((col) => col.column_name)
    .join(",");
};

export const getColsParamForModal = (cols) =>
  cols.filter((col) => col.showsummaryonly !== 'true').map((col) => col.column_name).join(",");
