/*===- TableGen'erated file -------------------------------------*- C++ -*-===*\
|*                                                                            *|
|* AttrDef Definitions                                                        *|
|*                                                                            *|
|* Automatically generated file, do not edit!                                 *|
|*                                                                            *|
\*===----------------------------------------------------------------------===*/

#ifdef GET_ATTRDEF_LIST
#undef GET_ATTRDEF_LIST

::mlir::acc::ClauseDefaultValueAttr,
::mlir::acc::ReductionOperatorAttr

#endif  // GET_ATTRDEF_LIST

#ifdef GET_ATTRDEF_CLASSES
#undef GET_ATTRDEF_CLASSES

static ::mlir::OptionalParseResult generatedAttributeParser(::mlir::AsmParser &parser, ::llvm::StringRef *mnemonic, ::mlir::Type type, ::mlir::Attribute &value) {
  return ::mlir::AsmParser::KeywordSwitch<::mlir::OptionalParseResult>(parser)
    .Case(::mlir::acc::ClauseDefaultValueAttr::getMnemonic(), [&](llvm::StringRef, llvm::SMLoc) {
      value = ::mlir::acc::ClauseDefaultValueAttr::parse(parser, type);
      return ::mlir::success(!!value);
    })
    .Case(::mlir::acc::ReductionOperatorAttr::getMnemonic(), [&](llvm::StringRef, llvm::SMLoc) {
      value = ::mlir::acc::ReductionOperatorAttr::parse(parser, type);
      return ::mlir::success(!!value);
    })
    .Default([&](llvm::StringRef keyword, llvm::SMLoc) {
      *mnemonic = keyword;
      return std::nullopt;
    });
}

static ::mlir::LogicalResult generatedAttributePrinter(::mlir::Attribute def, ::mlir::AsmPrinter &printer) {
  return ::llvm::TypeSwitch<::mlir::Attribute, ::mlir::LogicalResult>(def)    .Case<::mlir::acc::ClauseDefaultValueAttr>([&](auto t) {
      printer << ::mlir::acc::ClauseDefaultValueAttr::getMnemonic();
t.print(printer);
      return ::mlir::success();
    })
    .Case<::mlir::acc::ReductionOperatorAttr>([&](auto t) {
      printer << ::mlir::acc::ReductionOperatorAttr::getMnemonic();
t.print(printer);
      return ::mlir::success();
    })
    .Default([](auto) { return ::mlir::failure(); });
}

namespace mlir {
namespace acc {
namespace detail {
struct ClauseDefaultValueAttrStorage : public ::mlir::AttributeStorage {
  using KeyTy = std::tuple<::mlir::acc::ClauseDefaultValue>;
  ClauseDefaultValueAttrStorage(::mlir::acc::ClauseDefaultValue value) : value(value) {}

  KeyTy getAsKey() const {
    return KeyTy(value);
  }

  bool operator==(const KeyTy &tblgenKey) const {
    return (value == std::get<0>(tblgenKey));
  }

  static ::llvm::hash_code hashKey(const KeyTy &tblgenKey) {
    return ::llvm::hash_combine(std::get<0>(tblgenKey));
  }

  static ClauseDefaultValueAttrStorage *construct(::mlir::AttributeStorageAllocator &allocator, const KeyTy &tblgenKey) {
    auto value = std::get<0>(tblgenKey);
    return new (allocator.allocate<ClauseDefaultValueAttrStorage>()) ClauseDefaultValueAttrStorage(value);
  }

  ::mlir::acc::ClauseDefaultValue value;
};
} // namespace detail
ClauseDefaultValueAttr ClauseDefaultValueAttr::get(::mlir::MLIRContext *context, ::mlir::acc::ClauseDefaultValue value) {
  return Base::get(context, value);
}

::mlir::Attribute ClauseDefaultValueAttr::parse(::mlir::AsmParser &odsParser, ::mlir::Type odsType) {
  ::mlir::Builder odsBuilder(odsParser.getContext());
  ::llvm::SMLoc odsLoc = odsParser.getCurrentLocation();
  (void) odsLoc;
  ::mlir::FailureOr<::mlir::acc::ClauseDefaultValue> _result_value;

  // Parse variable 'value'
  _result_value = [&]() -> ::mlir::FailureOr<::mlir::acc::ClauseDefaultValue> {
      auto loc = odsParser.getCurrentLocation();
      ::llvm::StringRef enumKeyword;
      if (::mlir::failed(odsParser.parseKeyword(&enumKeyword)))
        return ::mlir::failure();
      auto maybeEnum = ::mlir::acc::symbolizeClauseDefaultValue(enumKeyword);
      if (maybeEnum)
        return *maybeEnum;
      return {(::mlir::LogicalResult)(odsParser.emitError(loc) << "expected " << "::mlir::acc::ClauseDefaultValue" << " to be one of: " << "present" << ", " << "none")};
    }();
  if (::mlir::failed(_result_value)) {
    odsParser.emitError(odsParser.getCurrentLocation(), "failed to parse DefaultValueAttr parameter 'value' which is to be a `::mlir::acc::ClauseDefaultValue`");
    return {};
  }
  assert(::mlir::succeeded(_result_value));
  return ClauseDefaultValueAttr::get(odsParser.getContext(),
      ::mlir::acc::ClauseDefaultValue((*_result_value)));
}

void ClauseDefaultValueAttr::print(::mlir::AsmPrinter &odsPrinter) const {
  ::mlir::Builder odsBuilder(getContext());
  odsPrinter << ' ';
  odsPrinter << stringifyClauseDefaultValue(getValue());
}

::mlir::acc::ClauseDefaultValue ClauseDefaultValueAttr::getValue() const {
  return getImpl()->value;
}

} // namespace acc
} // namespace mlir
MLIR_DEFINE_EXPLICIT_TYPE_ID(::mlir::acc::ClauseDefaultValueAttr)
namespace mlir {
namespace acc {
namespace detail {
struct ReductionOperatorAttrStorage : public ::mlir::AttributeStorage {
  using KeyTy = std::tuple<::mlir::acc::ReductionOperator>;
  ReductionOperatorAttrStorage(::mlir::acc::ReductionOperator value) : value(value) {}

  KeyTy getAsKey() const {
    return KeyTy(value);
  }

  bool operator==(const KeyTy &tblgenKey) const {
    return (value == std::get<0>(tblgenKey));
  }

  static ::llvm::hash_code hashKey(const KeyTy &tblgenKey) {
    return ::llvm::hash_combine(std::get<0>(tblgenKey));
  }

  static ReductionOperatorAttrStorage *construct(::mlir::AttributeStorageAllocator &allocator, const KeyTy &tblgenKey) {
    auto value = std::get<0>(tblgenKey);
    return new (allocator.allocate<ReductionOperatorAttrStorage>()) ReductionOperatorAttrStorage(value);
  }

  ::mlir::acc::ReductionOperator value;
};
} // namespace detail
ReductionOperatorAttr ReductionOperatorAttr::get(::mlir::MLIRContext *context, ::mlir::acc::ReductionOperator value) {
  return Base::get(context, value);
}

::mlir::Attribute ReductionOperatorAttr::parse(::mlir::AsmParser &odsParser, ::mlir::Type odsType) {
  ::mlir::Builder odsBuilder(odsParser.getContext());
  ::llvm::SMLoc odsLoc = odsParser.getCurrentLocation();
  (void) odsLoc;
  ::mlir::FailureOr<::mlir::acc::ReductionOperator> _result_value;
  // Parse literal '<'
  if (odsParser.parseLess()) return {};

  // Parse variable 'value'
  _result_value = [&]() -> ::mlir::FailureOr<::mlir::acc::ReductionOperator> {
      auto loc = odsParser.getCurrentLocation();
      ::llvm::StringRef enumKeyword;
      if (::mlir::failed(odsParser.parseKeyword(&enumKeyword)))
        return ::mlir::failure();
      auto maybeEnum = ::mlir::acc::symbolizeReductionOperator(enumKeyword);
      if (maybeEnum)
        return *maybeEnum;
      return {(::mlir::LogicalResult)(odsParser.emitError(loc) << "expected " << "::mlir::acc::ReductionOperator" << " to be one of: " << "add" << ", " << "mul" << ", " << "max" << ", " << "min" << ", " << "iand" << ", " << "ior" << ", " << "xor" << ", " << "eqv" << ", " << "neqv" << ", " << "land" << ", " << "lor")};
    }();
  if (::mlir::failed(_result_value)) {
    odsParser.emitError(odsParser.getCurrentLocation(), "failed to parse OpenACC_ReductionOperatorAttr parameter 'value' which is to be a `::mlir::acc::ReductionOperator`");
    return {};
  }
  // Parse literal '>'
  if (odsParser.parseGreater()) return {};
  assert(::mlir::succeeded(_result_value));
  return ReductionOperatorAttr::get(odsParser.getContext(),
      ::mlir::acc::ReductionOperator((*_result_value)));
}

void ReductionOperatorAttr::print(::mlir::AsmPrinter &odsPrinter) const {
  ::mlir::Builder odsBuilder(getContext());
  odsPrinter << "<";
  odsPrinter << stringifyReductionOperator(getValue());
  odsPrinter << ">";
}

::mlir::acc::ReductionOperator ReductionOperatorAttr::getValue() const {
  return getImpl()->value;
}

} // namespace acc
} // namespace mlir
MLIR_DEFINE_EXPLICIT_TYPE_ID(::mlir::acc::ReductionOperatorAttr)
namespace mlir {
namespace acc {

/// Parse an attribute registered to this dialect.
::mlir::Attribute OpenACCDialect::parseAttribute(::mlir::DialectAsmParser &parser,
                                      ::mlir::Type type) const {
  ::llvm::SMLoc typeLoc = parser.getCurrentLocation();
  ::llvm::StringRef attrTag;
  {
    ::mlir::Attribute attr;
    auto parseResult = generatedAttributeParser(parser, &attrTag, type, attr);
    if (parseResult.has_value())
      return attr;
  }
  
  parser.emitError(typeLoc) << "unknown attribute `"
      << attrTag << "` in dialect `" << getNamespace() << "`";
  return {};
}
/// Print an attribute registered to this dialect.
void OpenACCDialect::printAttribute(::mlir::Attribute attr,
                         ::mlir::DialectAsmPrinter &printer) const {
  if (::mlir::succeeded(generatedAttributePrinter(attr, printer)))
    return;
  
}
} // namespace acc
} // namespace mlir

#endif  // GET_ATTRDEF_CLASSES

