public readonly struct LaborTime
{
    public double Hours { get; }

    public LaborTime(double hours)
    {
        if (hours < 0) throw new ArgumentException("劳动时间不能为负数");
        Hours = hours;
    }

    // 允许直接转换为 double，方便计算
    public static implicit operator double(LaborTime time) => time.Hours;

    public override string ToString() => $"{Hours} 小时";
}