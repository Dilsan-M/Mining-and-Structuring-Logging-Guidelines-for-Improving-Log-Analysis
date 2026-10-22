package byolog

// Field represents a field for structured logging.
type Field struct {
	Name  string
	Value interface{}
}

// NewField creates a new field.
func NewField(name string, value interface{}) Field {
	return Field{Name: name, Value: value}
}

// Logger represents any structured logger.
type Logger interface {
	Error(msg string, fields ...Field)
	Warn(msg string, fields ...Field)
	Info(msg string, fields ...Field)
	Debug(msg string, fields ...Field)
	With(fields ...Field) Logger
	Named(name string) Logger
}

type nop struct{}

// Nop creates a logger which satisfies the interface and does nothing.
func Nop() Logger {
	return &nop{}
}

func (n *nop) Error(msg string, fields ...Field) {
}

func (n *nop) Warn(msg string, fields ...Field) {
}

func (n *nop) Info(msg string, fields ...Field) {
}

func (n *nop) Debug(msg string, fields ...Field) {
}

func (n *nop) With(fields ...Field) Logger {
	return n
}

func (n *nop) Named(name string) Logger {
	return n
}
