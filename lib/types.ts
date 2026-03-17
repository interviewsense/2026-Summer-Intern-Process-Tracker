export interface StageBreakdown {
  offer: number;
  rejection: number;
  interview: number;
  oa: number;
  question: number;
}

export interface Message {
  content: string;
  date: string;
  author: string;
  stage: keyof StageBreakdown;
}

export interface ThreadConvo {
  title: string;
  messages: { content: string; date: string; author: string }[];
}

export interface DailyCount {
  date: string;
  count: number;
}

export interface Company {
  name: string;
  count: number;
  stages: StageBreakdown;
  messages: Message[];
  threads: ThreadConvo[];
  daily: DailyCount[];
}

export interface TimelinePoint {
  date: string;
  offer?: number;
  rejection?: number;
  interview?: number;
  oa?: number;
  question?: number;
}

export interface RecentMessage {
  content: string;
  company: string | null;
  stage: string;
  date: string;
  author: string;
}

export interface InternData {
  generated: string;
  stats: {
    total_process_msgs: number;
    total_companies_tracked: number;
    total_offers: number;
    total_rejections: number;
    total_interviews: number;
    total_oas: number;
  };
  companies: Company[];
  timeline: TimelinePoint[];
  recent: RecentMessage[];
}
