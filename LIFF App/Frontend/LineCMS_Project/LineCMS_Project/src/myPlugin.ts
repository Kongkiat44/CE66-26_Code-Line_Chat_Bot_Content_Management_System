// variable that can import to use value
export const LINE_URL = "https://sprofile.line-scdn.net/"
export const IP_API_URL: string = "https://analytics02.kmitl.ac.th";
export const API_URL: string = "https://analytics02.kmitl.ac.th";

// function that can import to use function
export function remove_LINE_URL(a: string): string{
  return a.replace(LINE_URL, "")
}

export function insert_LINE_URL(a: string): string{
  return LINE_URL + a
}

export function remove_API_URL(a: string): string{
  return a.replace(API_URL, "")
}

export function insert_API_URL(a: string): string{
  return API_URL + a
}