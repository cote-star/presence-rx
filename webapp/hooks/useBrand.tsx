"use client";

import {
  createContext,
  useContext,
  useState,
  useEffect,
  useCallback,
  type ReactNode,
} from "react";
import type { BrandData, BrandConfig } from "@/lib/types";

interface BrandContextValue {
  brands: string[];
  currentBrand: string;
  switchBrand: (caseId: string) => void;
  data: BrandData | null;
  config: BrandConfig | null;
  loading: boolean;
}

const BrandContext = createContext<BrandContextValue>({
  brands: [],
  currentBrand: "nothing-phone",
  switchBrand: () => {},
  data: null,
  config: null,
  loading: true,
});

export function BrandProvider({ children }: { children: ReactNode }) {
  const [brands, setBrands] = useState<string[]>([]);
  const [currentBrand, setCurrentBrand] = useState("nothing-phone");
  const [data, setData] = useState<BrandData | null>(null);
  const [config, setConfig] = useState<BrandConfig | null>(null);
  const [loading, setLoading] = useState(true);
  const [cache, setCache] = useState<Record<string, BrandData>>({});
  const [configCache, setConfigCache] = useState<Record<string, BrandConfig>>({});

  // Resolve basePath for data fetches (works on GitHub Pages /presence-rx/)
  const base = process.env.NEXT_PUBLIC_BASE_PATH || "";

  // Load brand registry on mount
  useEffect(() => {
    fetch(`${base}/data/brands.json`)
      .then((r) => r.json())
      .then((d) => setBrands(d.brands || []))
      .catch(() => setBrands(["nothing-phone", "attio", "bmw"]));
  }, [base]);

  // Load brand data when switching
  const loadBrand = useCallback(
    async (caseId: string) => {
      setLoading(true);

      // Check cache
      if (cache[caseId]) {
        setData(cache[caseId]);
        setConfig(configCache[caseId] || null);
        setLoading(false);
        return;
      }

      try {
        const [dataRes, configRes] = await Promise.all([
          fetch(`${base}/data/${caseId}.json`),
          fetch(`${base}/data/${caseId}-config.json`),
        ]);

        const brandData: BrandData = await dataRes.json();
        setData(brandData);
        setCache((prev) => ({ ...prev, [caseId]: brandData }));

        if (configRes.ok) {
          const brandConfig: BrandConfig = await configRes.json();
          setConfig(brandConfig);
          setConfigCache((prev) => ({ ...prev, [caseId]: brandConfig }));
        }
      } catch (err) {
        console.error(`Failed to load brand ${caseId}:`, err);
      } finally {
        setLoading(false);
      }
    },
    [cache, configCache]
  );

  // Load initial brand
  useEffect(() => {
    loadBrand(currentBrand);
  }, []); // eslint-disable-line react-hooks/exhaustive-deps

  const switchBrand = useCallback(
    (caseId: string) => {
      setCurrentBrand(caseId);
      loadBrand(caseId);
    },
    [loadBrand]
  );

  return (
    <BrandContext.Provider
      value={{ brands, currentBrand, switchBrand, data, config, loading }}
    >
      {children}
    </BrandContext.Provider>
  );
}

export function useBrand() {
  return useContext(BrandContext);
}
