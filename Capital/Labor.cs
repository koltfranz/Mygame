
namespace Captial;

public enum LaborType
{
    SimpleLabor,  // 简单劳动
    ComplexLabor  // 复杂劳动
}
public class Labor
{
    /// <summary>
    /// 具体劳动
    /// </summary>
    public required string ConcreteLabor { get; set; } // 具体劳动是质的定义
    /// <summary>
    /// 抽象劳动
    /// </summary>
    public LaborTime AbstractLabor { get; set; }//抽象劳动只有量的区别

    //我将所有劳动都视作复杂劳动，简单劳动则是作为抽象的单位，也就是说即使它是简单劳动，也只是一倍的简单劳动。
    /// <summary>
    /// 简单劳动向复杂劳动转化的倍数
    /// </summary>
    public double K { get; init; }
    /// <summary>
    /// 劳动类型，是简单劳动还是复杂劳动
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
