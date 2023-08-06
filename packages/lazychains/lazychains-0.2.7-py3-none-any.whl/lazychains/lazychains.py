from typing import TypeVar, Generic, Tuple, Union, Any
from collections.abc import Iterable, Iterator

T = TypeVar('T')

class Chain(Generic[T]):
    """
    A chain of items is made up of a singly linked list of Chain records. 
    Each Chain record *either* holds a single item and a pointer to the 
    subsequent chain of items *or* will be an end-of-chain marker *or* 
    holds an iterator that will be run on demand.

    Usually they are less compact than arrays or tuples, which is why they
    are less popular. However their ability to share "tails" can sometimes
    help us avoid unnecessary copying, saving time and store. Also, they can 
    easily represent a large or even infinite sequence that is expanded on 
    demand. Here's a typical idioms showing how to efficiently represent all 
    the lines from a file:

    .. code:: python

        lines = lazychain( open( 'myfile.txt', 'r' ) )
        while lines:
            #
            # Process one or more lines (not shown)
            ...
            lines = lines.tail()

    Note how this idiom 'walks' the chain, overwriting the lines variable 
    so as to allow the Chain records to be swiftly reclaimed by the store
    manager.
    """

    # Implementation note: the _back field is used to represent different 
    # states of the chain. This implementation technique, borrowed from the
    # implementation of dynamic lists in Poplog, requires only 2 fields and
    # has the advantage of overwriting unwanted references to the iterator, 
    # which therefore is released as soon as the chain is fully expanded.
    #
    #   True - this is an unexpanded node with the _front being the iterator
    #   Ellipsis - this is an unexpanded node with the _front being a deferred call
    #   False - this is an expanded _empty_ node, the front is ignored
    #   Chain - this is an expended _nonempty_ node, the front is the value
    #
    # It is an key fact that after bool(mychain) tests positive, it is safe to 
    # use _front/_back as synonyms for head()/tail(). Within the class this is 
    # used pervasively to avoid the overhead of a method call.

    def __init__( self, head, tail ):
        """Private constructor
        :meta private:
        """
        self._front = head
        self._back = tail

    def __bool__( self ) -> bool:
        """
        True if the chain has any members, otherwise False. Will expand
        this chain node if required.
        """
        while True:
            if self._back is True:
                try:
                    item = next( self._front )
                    c: Chain[T] = Chain( self._front, True )
                    self._front = item
                    self._back = c
                except StopIteration:
                    self._back = False
                    self._front = None
                    break
            elif self._back is Ellipsis:
                c = self._front()
                if isinstance( c, Chain ):
                    self._front = c._front
                    self._back = c._back
                else:
                    raise Exception(f"Lazycall did not return a chain: {c}")
            else:
                break

        return self._back is not False

    def is_expanded( self ) -> bool:
        """
        Returns True if the Chain node is expanded and either the member is 
        already cached or the node represents the empty list. Returns False if
        the Chain node will need to run an iterator to determine its contents.
        This should hardly ever be used in application programs. However it
        can be useful when trying to debug.
        """
        return self._back is not True and self._back is not Ellipsis

    def expanded_len( self ):
        """
        Returns the number of expanded nodes in the chain. It is not 
        expected that this would be used in typical programming but it is
        handy for debugging.
        """
        c = self
        n = 0
        while c.is_expanded() and c:
            c = c._back
            n += 1
        return n
        
    def head( self ) -> T:
        """
        Returns the first item in the chain.
        """
        if self:
            return self._front
        else:
            raise Exception('Trying to take the head of an empty Chain')

    def tail( self ) -> 'Chain[T]':
        """
        Returns the chain that represents all but the first item. Chains
        form singly linked lists, so this is a fast operation that always
        yields the same result when applied to the same chain.
        """
        if self:
            return self._back
        else:
            raise Exception('Trying to take the tail of an empty Chain')

    def dest( self ) -> Tuple[ T, 'Chain[T]' ]:
        """
        Returns both the head and tail in one operation. This performs the
        expansion check exactly once, so is potentially slightly more 
        efficent - but more importantly it often makes the code easier to
        read.
        """
        if self:
            return self._front, self._back
        else:
            raise Exception('Trying to take the head and tail of an empty Chain')

    def new( self, x: T ) -> 'Chain[T]':
        """
        Allocates a new chain node with x as its head and the current chain
        as its tail.
        """
        return Chain( x, self )

    def lazycall( self, f, *args ):
        r"""
        This is useful when writing recursive lazy functions. It
        returns a Chain node that represents a deferred call of f( self, \*args ).
        The call must return a Chain. N.B. It may return another lazy-chain but,
        if so, it will recursively be forced.
        """
        return lazycall( lambda: f( self, *args ) )

    def map( self, f, *iterables ):
        r"""
        This works exactly like the built in function map except that it
        returns a Chain rather than an iterable. If you only need an iterable
        returned just do this: map( f, chain, \*iterables )
        """
        return lazychain( map( f, self, *iterables ) )

    def filter( self, predicate ):
        """
        This works exactly like the built in function filter except that it
        returns a Chain rather than an iterable. If you only need an iterable
        returned just do this: filter( f, chain )
        """
        return lazychain( filter( predicate, self ) )

    def zip( self, *iterables, strict=False ):
        r"""
        This works exactly like the built in function zip except that it
        returns a Chain of tuples rather than an iterable of tuples. If you only 
        need an iterable returned just do this: zip( chain, \*iterables, strict )
        """
        return lazychain( zip( self, *iterables, strict=strict ) )

    def __iter__( self ):
        """
        Returns an iterator over all the items in the chain. This will 
        gradually expand the underlying chain.
        """
        _chain = self
        while _chain:
            yield _chain._front
            _chain = _chain._back

    def __len__( self ) -> int:
        """
        Returns a count of the number of items in a chain, which also forces
        the expansion of the whole chain. If the chain is infinite this will
        not terminate!
        """
        c = self
        n = 0
        while c:
            n += 1
            c = c._back
        return n

    def len_is_at_least( self, n:int ) -> bool:
        """
        Returns True if the chain is at least n items in length. This avoids
        expanding the whole chain. Otherwise returns False.
        """
        c = self
        while n > 0:
            if not c:
                return False
            c = c._back
            n -= 1
        return True

    def len_is_more_than( self, n:int ) -> bool:
        """
        Returns True if the chain is more than n in length. This avoids
        expanding the whole chain. Otherwise returns False.
        """
        return self.len_is_at_least( n + 1)

    def len_is_at_most( self, n:int ) -> bool:
        """
        Returns True if the chain has length at most n. This avoids
        expanding the whole chain. Otherwise returns False.
        """
        return not self.len_is_more_than( n )

    def len_is_less_than( self, n:int ) -> bool:
        """
        Returns True if the length of the chain is less than n. This avoids
        expanding the whole chain. Otherwise returns False.
        """
        return not self.len_is_at_least( n )

    def __contains__( self, x:T ) -> bool:
        """
        Returns True if x is an element of the Chain, otherwise False.
        """
        c = self
        while c:
            if c._front == x:
                return True
            c = c._back
        return False

    def expand( self ):
        """
        Force the expansion of the chain, returning the chain.
        """
        c = self
        while c:
            c = c._back
        return self

    def __add__( self, it: Iterable[T] ) -> 'Chain[T]':
        """
        Construct a new chain that consists of the concatenation of all the
        items in self followed by all the items from it. Note that self is
        expanded but the supplied iterable/iterator is not.
        """
        if not isinstance( it, Chain ):
            it = Chain( iter(it), True )
        c = self
        r: Chain[T] = Chain( None, False )
        while c:
            r = Chain( c._front, r )
            c = c._back
        while r:
            it = Chain( r._front, it )
            r = r._back
        return it

    def __getitem__( self, n:int ):
        """
        Returns the k-th item in the Chain, provided that the Chain is longer
        than k. Note that this will traverse k nodes before returning an answer
        and hence is potentially slow. If the Chain does not have enough elements
        then an exception is raised.

        Negative indexes are accepted and have the usual meaning of indexing
        from the end. Because this involves calculating the length of the chain,
        it is inherently slow and obviously unsafe on infinite or extremely long
        chains.
        """
        if n >= 0:
            c = self
            k = n
            while k > 0:
                if c:
                    k -= 1
                    c = c._back
                else:
                    break
            if c:
                return c._front
            else:
                raise IndexError(f'Index is out of bounds for chain: {n}') 
        elif n < 0:
            L = len( self )
            idx = L + n
            if idx >= 0:
                return self.__getitem__( idx )
            else:
                raise IndexError(f'Negative index is out of bounds for chain: {n}')
        else:
            raise IndexError(f'Invalid index for chain: {n}')

    def __repr__( self ):
        items = []
        c = self
        while c.is_expanded() and c:
            items.append( repr( c._front ) )
            c = c._back
        if not c.is_expanded():
            items.append('...')    
        return f"chain([{','.join(items)}])"


"""
We commonly construct empty chains, which are immutable. So we can (and should) 
share a single empty chain where possible. NIL points the value we reuse.
"""
NIL: Chain[Any] = Chain( None, False )

def lazychain( it:Iterable[T]=() ) -> Chain[T]:
    """
    Returns an unexpanded chain based on the iterable/iterator. Using this
    constructor allows you to work with very large or even infinite chains.
    Note that because this is lazy, subsequent changes to the underlying 
    iterable maybe incorporated into the chain.
    """
    if it == ():
        return NIL
    return Chain( iter(it), True )

def chain( it:Iterable[T]=() ) -> Chain[T]:
    """
    Returns a fully expanded chain based on the iterable/iterator. This is 
    useful when you need the chain to be independent of changes in the 
    underlying iterable.
    """
    if it == ():
        return NIL
    return lazychain( it ).expand()

def lazycall( f, *args ) -> Chain[T]:
    r"""
    This method implements a lazy call of a function f that returns a Chain.
    This is useful when processing potentially infinite lists. Strictly speaking 
    it takes a function f that, when applied to \*args, returns a Chain. When that
    Chain is expanded, the function f is automatically called and the resulting
    Chain overwrites it. If necessary the Chain is repeatedly expanded.
    """
    return Chain( f, Ellipsis )
