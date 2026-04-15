namespace Capital;

/// <summary>
/// 劳动时间单位枚举
/// 马克思《资本论》中，价值量以劳动时间计算，这里以小时为基准单位
/// </summary>
public enum LaborTimeUnit
{
    /// <summary>小时：价值计量的基准单位</summary>
    Hour = 1,

    /// <summary>分钟：1小时 = 60分钟</summary>
    Minute = 60,

    /// <summary>秒：1小时 = 3600秒</summary>
    Second = 3600
}

/// <summary>
/// 劳动时间结构体（不可变）
/// 价值量由劳动时间决定，这是政治经济学的基本原理
/// </summary>
public readonly struct LaborTime
{
    /// <summary>小时数</summary>
    public double Hours { get; }

    /// <summary>
    /// 构造函数
    /// </summary>
    /// <param name="hours">小时数，必须为非负数</param>
    /// <exception cref="ArgumentException">劳动时间不能为负数</exception>
    public LaborTime(double hours)
    {
        if (hours < 0) throw new ArgumentException("劳动时间不能为负数");
        Hours = hours;
    }

    /// <summary>
    /// 隐式转换为 double，方便计算
    /// 例如：double h = laborTime; 直接获取小时数
    /// </summary>
    public static implicit operator double(LaborTime time) => time.Hours;

    /// <summary>
    /// 重写 ToString，返回易读格式
    /// </summary>
    public override string ToString() => $"{Hours} 小时";
}

/// <summary>
/// 劳动类型枚举
/// </summary>
public enum LaborType
{
    /// <summary>简单劳动：无需专门训练，一般人都能从事的劳动</summary>
    SimpleLabor,

    /// <summary>复杂劳动：需要专门训练才能从事的劳动</summary>
    ComplexLabor
}

/// <summary>
/// 劳动类
///
/// 马克思政治经济学中劳动的二重性：
/// 1. 具体劳动（ConcreteLabor）：劳动的质的方面，如耕种、狩猎、纺织等
/// 2. 抽象劳动（AbstractLabor）：劳动的量的方面，无差别的人类劳动
///
/// 简单劳动与复杂劳动：
/// - 简单劳动作为基准单位，K=1
/// - 复杂劳动通过K值转化为简单劳动的等价量
/// - 例如：1小时复杂劳动(K=2) = 2小时简单劳动
/// </summary>
public class Labor
{
    /// <summary>
    /// 具体劳动
    /// 反映劳动的具体形式，如"狩猎"、"采集"、"纺织"等
    /// 不同具体劳动创造不同的使用价值
    /// </summary>
    public required string ConcreteLabor { get; set; }

    /// <summary>
    /// 抽象劳动
    /// 凝结在商品中的无差别的人类劳动，是价值的源泉
    /// 只有量的区别，1小时劳动就是1小时劳动
    /// </summary>
    public LaborTime AbstractLabor { get; set; }

    /// <summary>
    /// 简单劳动向复杂劳动转化的倍数
    /// - K = 1：简单劳动，无需专门训练
    /// - K > 1：复杂劳动，需要专门训练或技能
    ///
    /// 马克思观点：复杂劳动是多倍简单劳动的浓缩
    /// 计算公式：抽象劳动时间 = 具体劳动时间 × K
    /// </summary>
    public double K { get; init; }

    /// <summary>
    /// 劳动类型（根据K值自动判断）
    /// K = 1 返回 SimpleLabor，K > 1 返回 ComplexLabor
    /// </summary>
    public LaborType LaborType
    {
        get
        {
            if (K == 1)
            {
                return LaborType.SimpleLabor;
            }
            return LaborType.ComplexLabor;
        }
    }
}
