import { useQuery } from '@tanstack/react-query';
import axios from 'axios';

export function useSearchSemanticGroups(params?: Record<string, any>) {
  return useQuery({
    queryKey: ['search-semantic-groups', params],
    queryFn: async () => {
      const response = await axios.get('/search/semantic-groups', { params });
      return response.data;
    },
    enabled: !!params
  });
} 