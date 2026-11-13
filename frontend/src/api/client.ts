import axios from 'axios';
const client=axios.create({baseURL:import.meta.env.VITE_API_BASE_URL||'http://localhost:8000/api'});
client.interceptors.request.use(c=>{const t=localStorage.getItem('access_token');if(t)c.headers.Authorization=`Bearer ${t}`;return c});
export default client;
