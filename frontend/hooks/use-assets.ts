import { useState, useEffect, useCallback, useRef } from 'react';
import { api } from '@/lib/api';
import { 
  Asset, 
  AssetCreate, 
  AssetUpdate, 
  AssetAssignment, 
  AssetAssignmentCreate,
  AssetListParams,
  PaginatedAssetResponse,
  AssetStatistics,
  AssetType,
  AssetStatus,
  Location
} from '@/lib/types';

interface UseAssetsOptions {
  immediate?: boolean;
  onSuccess?: (data: any) => void;
  onError?: (error: Error) => void;
}

interface UseAssetsReturn {
  // Asset list operations
  assets: Asset[];
  loading: boolean;
  error: Error | null;
  refetch: () => void;
  
  // Pagination
  pagination: {
    page: number;
    size: number;
    total: number;
    hasNext: boolean;
    hasPrevious: boolean;
  };
  
  // Filtering and sorting
  filters: AssetListParams;
  setFilters: (filters: Partial<AssetListParams>) => void;
  
  // CRUD operations
  createAsset: (asset: AssetCreate) => Promise<Asset>;
  updateAsset: (id: number, asset: AssetUpdate) => Promise<Asset>;
  deleteAsset: (id: number) => Promise<void>;
  getAsset: (id: number) => Promise<Asset>;
  
  // Assignment operations
  assignAsset: (assignment: AssetAssignmentCreate) => Promise<AssetAssignment>;
  returnAsset: (assignmentId: number, update: Partial<AssetAssignment>) => Promise<AssetAssignment>;
  
  // Lookup data
  assetTypes: AssetType[];
  assetStatuses: AssetStatus[];
  locations: Location[];
  
  // Statistics
  statistics: AssetStatistics | null;
  statisticsLoading: boolean;
  statisticsError: Error | null;
  
  // Utility functions
  isLoading: boolean;
  hasError: boolean;
}

export function useAssets(options: UseAssetsOptions = {}): UseAssetsReturn {
  const { immediate = true, onSuccess, onError } = options;
  
  // Keep stable refs to the callbacks so they don't trigger useEffect loops
  const onSuccessRef = useRef<typeof onSuccess | null>(null);
  const onErrorRef = useRef<typeof onError | null>(null);

  useEffect(() => {
    onSuccessRef.current = onSuccess ?? null;
  }, [onSuccess]);

  useEffect(() => {
    onErrorRef.current = onError ?? null;
  }, [onError]);
  
  // State for assets list
  const [assets, setAssets] = useState<Asset[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<Error | null>(null);
  
  // State for pagination
  const [pagination, setPagination] = useState({
    page: 1,
    size: 20,
    total: 0,
    hasNext: false,
    hasPrevious: false,
  });
  
  // State for filters
  const [filters, setFilters] = useState<AssetListParams>({
    skip: 0,
    limit: 20,
  });
  
  // State for lookup data
  const [assetTypes, setAssetTypes] = useState<AssetType[]>([]);
  const [assetStatuses, setAssetStatuses] = useState<AssetStatus[]>([]);
  const [locations, setLocations] = useState<Location[]>([]);
  
  // State for statistics
  const [statistics, setStatistics] = useState<AssetStatistics | null>(null);
  const [statisticsLoading, setStatisticsLoading] = useState(false);
  const [statisticsError, setStatisticsError] = useState<Error | null>(null);
  
  // Fetch assets with current filters
  const fetchAssets = useCallback(async () => {
    setLoading(true);
    setError(null);
    
    try {
      const queryParams = new URLSearchParams();
      
      // Add pagination params
      if (filters.skip !== undefined) queryParams.append('skip', filters.skip.toString());
      if (filters.limit !== undefined) queryParams.append('limit', filters.limit.toString());
      
      // Add filter params
      if (filters.asset_type_id) queryParams.append('asset_type_id', filters.asset_type_id.toString());
      if (filters.status_code) queryParams.append('status_code', filters.status_code);
      if (filters.location_id) queryParams.append('location_id', filters.location_id.toString());
      if (filters.search) queryParams.append('search', filters.search);
      
      // Add sort params
      if (filters.sort_by) queryParams.append('sort_by', filters.sort_by);
      if (filters.sort_order) queryParams.append('sort_order', filters.sort_order);
      
      const endpoint = `/api/assets?${queryParams.toString()}`;
      const response = await api.get<any>(endpoint);

      // Handle both paginated and simple list responses
      if (Array.isArray(response)) {
        // Backend returned a plain list
        setAssets(response);
        setPagination({
          page: 1,
          size: response.length,
          total: response.length,
          hasNext: false,
          hasPrevious: false,
        });
      } else {
        // Backend returned paginated structure
        setAssets(response.items);
        setPagination({
          page: response.page,
          size: response.size,
          total: response.total_count,
          hasNext: response.has_next,
          hasPrevious: response.has_previous,
        });
      }
      
      onSuccessRef.current?.(response);
    } catch (err) {
      const error = err instanceof Error ? err : new Error('Failed to fetch assets');
      setError(error);
      onErrorRef.current?.(error);
    } finally {
      setLoading(false);
    }
  }, [filters]);
  
  // Fetch lookup data
  const fetchLookupData = useCallback(async () => {
    try {
      const [typesResponse, statusesResponse, locationsResponse] = await Promise.all([
        api.get<AssetType[]>('/api/assets/types'),
        api.get<AssetStatus[]>('/api/assets/statuses'),
        api.get<Location[]>('/api/locations'),
      ]);
      
      setAssetTypes(typesResponse);
      setAssetStatuses(statusesResponse);
      setLocations(locationsResponse);
    } catch (err) {
      console.error('Failed to fetch lookup data:', err);
    }
  }, []);
  
  // Fetch statistics
  const fetchStatistics = useCallback(async () => {
    setStatisticsLoading(true);
    setStatisticsError(null);
    
    try {
      const response = await api.get<AssetStatistics>('/api/assets/statistics');
      setStatistics(response);
    } catch (err) {
      const error = err instanceof Error ? err : new Error('Failed to fetch statistics');
      setStatisticsError(error);
    } finally {
      setStatisticsLoading(false);
    }
  }, []);
  
  // CRUD operations
  const createAsset = useCallback(async (asset: AssetCreate): Promise<Asset> => {
    const response = await api.post<Asset>('/api/assets', asset);
    await fetchAssets(); // Refresh the list
    return response;
  }, [fetchAssets]);
  
  const updateAsset = useCallback(async (id: number, asset: AssetUpdate): Promise<Asset> => {
    const response = await api.put<Asset>(`/api/assets/${id}`, asset);
    await fetchAssets(); // Refresh the list
    return response;
  }, [fetchAssets]);
  
  const deleteAsset = useCallback(async (id: number): Promise<void> => {
    await api.delete(`/api/assets/${id}`);
    await fetchAssets(); // Refresh the list
  }, [fetchAssets]);
  
  const getAsset = useCallback(async (id: number): Promise<Asset> => {
    return await api.get<Asset>(`/api/assets/${id}`);
  }, []);
  
  // Assignment operations
  const assignAsset = useCallback(async (assignment: AssetAssignmentCreate): Promise<AssetAssignment> => {
    const response = await api.post<AssetAssignment>('/api/assets/assignments', assignment);
    await fetchAssets(); // Refresh the list
    return response;
  }, [fetchAssets]);
  
  const returnAsset = useCallback(async (assetId: number, returnData: any): Promise<AssetAssignment> => {
    const response = await api.post<AssetAssignment>(`/api/assets/${assetId}/return`, returnData);
    await fetchAssets(); // Refresh the list
    return response;
  }, [fetchAssets]);
  
  // Update filters
  const updateFilters = useCallback((newFilters: Partial<AssetListParams>) => {
    setFilters(prev => ({
      ...prev,
      ...newFilters,
      // Reset to first page when filters change
      skip: newFilters.skip !== undefined ? newFilters.skip : 0,
    }));
  }, []);
  
  // Refetch function
  const refetch = useCallback(() => {
    fetchAssets();
    fetchStatistics();
  }, [fetchAssets, fetchStatistics]);
  
  // Initialize data
  useEffect(() => {
    if (immediate) {
      fetchAssets();
      fetchLookupData();
      fetchStatistics();
    }
  }, [immediate, fetchAssets, fetchLookupData, fetchStatistics]);
  
  // Refetch when filters change
  useEffect(() => {
    if (immediate) {
      fetchAssets();
    }
  }, [filters, immediate, fetchAssets]);
  
  return {
    // Asset list operations
    assets,
    loading,
    error,
    refetch,
    
    // Pagination
    pagination,
    
    // Filtering and sorting
    filters,
    setFilters: updateFilters,
    
    // CRUD operations
    createAsset,
    updateAsset,
    deleteAsset,
    getAsset,
    
    // Assignment operations
    assignAsset,
    returnAsset,
    
    // Lookup data
    assetTypes,
    assetStatuses,
    locations,
    
    // Statistics
    statistics,
    statisticsLoading,
    statisticsError,
    
    // Utility
    isLoading: loading || statisticsLoading,
    hasError: !!error || !!statisticsError,
  };
} 