namespace Captial;

public class Commodity
{
    /// <summary>
    /// 名字
    /// </summary>
    public required string Name { get; set; }
    /// <summary>
    /// 使用价值，是商品本身
    /// </summary>
    public Commodity UseValue
    {
        get { return this; }
    }
    /// <summary>
    /// 有用性
    /// </summary>
    public required string Usefulness { get; set; }
    /// <summary>
    /// 交换价值
    /// </summary>
    /// <param name="commodity"></param>
    /// <returns></returns>
    public string Exchange(Commodity commodity)
    {
        return ("可以交换多少个");
    }
    private LaborTime _value;
    private Labor _labor = null!;
    private bool _valueSetDirectly;

    /// <summary>
    /// 价值（直接设定后反向推导抽象劳动，或从抽象劳动赋值）
    /// </summary>
    public LaborTime Value
    {
        get => _value;
        set
        {
            _value = value;
            _valueSetDirectly = true;
            _labor.AbstractLabor = value;
        }
    }

    public required Labor Labor
    {
        get => _labor;
        set
        {
            _labor = value;
            if (!_valueSetDirectly)
            {
                _value = _labor.AbstractLabor;
            }
        }
    }

    



}
